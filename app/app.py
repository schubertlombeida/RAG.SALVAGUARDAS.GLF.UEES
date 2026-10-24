"""Interfaz académica: búsqueda local o RAG remoto autenticado del portal."""
import os
import re
from time import perf_counter
from urllib.parse import urlsplit
import requests
from flask import Flask, jsonify, render_template, request
from src.model import BM25
from src.utils import ROOT, read_jsonl

EXAMPLES = ["¿Qué actividades excluye el GLF?", "¿Qué es el PGAS?", "¿Cómo se clasifican los riesgos ambientales y sociales?"]

def validate_remote(data):
    if not isinstance(data, dict) or not isinstance(data.get("generated"), bool):
        raise ValueError("Respuesta remota inválida")
    results = data.get("results", [])
    sources = data.get("sources", [])
    if not isinstance(results, list) or not isinstance(sources, list):
        raise ValueError("Las referencias deben ser listas")
    if len(results) > 5 or len(sources) > 5:
        raise ValueError("Demasiadas referencias")
    by_id = {r["chunk_id"]: r for r in results}
    if len(by_id) != len(results) or len({s["chunk_id"] for s in sources}) != len(sources):
        raise ValueError("Referencias duplicadas")
    if not data.get("answer") or (data["generated"] and not sources) or (not data["generated"] and sources):
        raise ValueError("Respuesta y citas incompatibles")
    for row in results + sources:
        url = urlsplit(row["source_url"])
        if url.scheme != "https" or url.hostname != "galapagoslifefund.org.ec" or url.username or url.password:
            raise ValueError("Fuente no permitida")
        if type(row["page"]) is not int or row["page"] < 1:
            raise ValueError("Página inválida")
    for source in sources:
        original = by_id.get(source["chunk_id"])
        if original is None or any(source.get(k) != original.get(k) for k in ["document_id", "source_url", "page"]):
            raise ValueError("La cita no corresponde al pasaje")
        if f"[{source['chunk_id']}]" not in data["answer"]:
            raise ValueError("La referencia no aparece en la respuesta")
    cited = set(re.findall(r"\[([^\[\]]+)\]", data["answer"]))
    known = {s["chunk_id"] for s in sources}
    if data["generated"] and cited != known:
        raise ValueError("La respuesta contiene referencias no verificadas")
    return data

def create_app(index=None, transport=None):
    app = Flask(__name__, template_folder="templates", static_folder="assets")
    app.config["MAX_CONTENT_LENGTH"] = 8192
    if index is None:
        corpus = ROOT / "data/processed/chunks.jsonl"
        index = BM25(read_jsonl(corpus)) if corpus.exists() else None
    post = transport or requests.post

    @app.get("/")
    def home():
        return render_template("index.html", examples=EXAMPLES)

    @app.get("/healthz")
    def health():
        return jsonify({"ok": index is not None, "local_retrieval": True,
                        "remote_rag_configured": bool(os.getenv("GLF_RAG_URL"))})

    @app.post("/api/query")
    def query():
        payload = request.get_json(silent=True)
        value = payload.get("query") if isinstance(payload, dict) else None
        mode = payload.get("mode", "local") if isinstance(payload, dict) else None
        if not isinstance(value, str) or not 3 <= len(value.strip()) <= 600 or mode not in ["local", "rag"]:
            return jsonify(error="Escriba entre 3 y 600 caracteres y seleccione un modo válido."), 400
        value = value.strip()
        start = perf_counter()
        if mode == "rag":
            endpoint = os.getenv("GLF_RAG_URL", "")
            parsed = urlsplit(endpoint)
            if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".hf.space") or parsed.username or parsed.password:
                return jsonify(error="Configure el servicio RAG en el servidor. Puede utilizar la búsqueda local."), 503
            try:
                response = post(endpoint, json={"query": value}, headers={"X-Demo-Key": os.getenv("GLF_RAG_KEY", "")},
                                timeout=55, allow_redirects=False)
                response.raise_for_status()
                result = validate_remote(response.json())
                return jsonify(result)
            except (requests.RequestException, ValueError, KeyError, TypeError):
                return jsonify(error="El servicio RAG no respondió con evidencia válida. Intente más tarde."), 502
        if index is None:
            return jsonify(error="Prepare el corpus con python -m src.data_processing antes de consultar."), 503
        rows = index.search(value, 5)
        return jsonify({"generated": False, "answer": "Pasajes recuperados para revisión. Esta búsqueda local no genera una respuesta con IA.",
                        "results": rows, "sources": [], "mode": "local_retrieval",
                        "timings": {"total_seconds": perf_counter()-start}})

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'"
        return response
    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8766, debug=False)
