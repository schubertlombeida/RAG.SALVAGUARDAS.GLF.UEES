"""Interfaz académica: búsqueda local o RAG remoto autenticado del portal."""
import os
import re
import json
from uuid import uuid4
from time import perf_counter
from urllib.parse import urlsplit
import requests
from flask import Flask, jsonify, render_template, request, Response, stream_with_context
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
    if not isinstance(data.get("answer"), str) or len(data["answer"]) > 20000:
        raise ValueError("Texto de respuesta inválido")
    for row in results + sources:
        if not isinstance(row, dict) or any(not isinstance(row.get(key), str) or not row[key] or len(row[key]) > 20000 for key in ["chunk_id", "document_id", "source_name", "source_url"]):
            raise ValueError("Pasaje inválido")
    if any(not isinstance(r.get("text"), str) or not r["text"] or len(r["text"]) > 20000 for r in results):
        raise ValueError("Texto de evidencia inválido")
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
        if original is None or any(source.get(k) != original.get(k) for k in ["document_id", "source_name", "source_url", "page"]):
            raise ValueError("La cita no corresponde al pasaje")
        if f"[{source['chunk_id']}]" not in data["answer"]:
            raise ValueError("La referencia no aparece en la respuesta")
    cited = set(re.findall(r"\[([^\[\]]+)\]", data["answer"]))
    known = {s["chunk_id"] for s in sources}
    if data["generated"] and cited != known:
        raise ValueError("La respuesta contiene referencias no verificadas")
    detail = data.get("diagnostics")
    if data.get("answer_mode", "brief") not in ("brief", "expanded"):
        raise ValueError("Modalidad inválida")
    if detail is not None:
        if not isinstance(detail, dict): raise ValueError("Diagnóstico inválido")
        if not isinstance(detail.get("corpus_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", detail["corpus_sha256"]): raise ValueError("Corpus inválido")
        for key, maximum in [("context_chars",18000),("max_output_tokens",1500),("provider_attempts",2)]:
            if type(detail.get(key)) is not int or not 0 <= detail[key] <= maximum: raise ValueError("Límite de diagnóstico inválido")
        for key in ("input_tokens", "output_tokens"):
            if detail.get(key) is not None and (type(detail[key]) is not int or not 0 <= detail[key] <= 2000000): raise ValueError("Consumo inválido")
        if type(detail.get("usage_complete")) is not bool: raise ValueError("Consumo inválido")
        if detail["usage_complete"] and (detail["provider_attempts"] == 0 or detail.get("input_tokens") is None or detail.get("output_tokens") is None): raise ValueError("Consumo incompleto")
        context_ids = detail.get("context_ids")
        if not isinstance(context_ids, list) or len(context_ids)>5 or len(set(context_ids)) != len(context_ids) or not set(context_ids) <= by_id.keys() or not known <= set(context_ids): raise ValueError("Contexto incompatible")
        for key in ("policy_version", "retrieval_method"):
            if not isinstance(detail.get(key), str) or not 1 <= len(detail[key]) <= 100: raise ValueError("Versión inválida")
        if detail.get("finish_reason") not in ("stop", "length", "content_filter", "tool_calls", "not_reported"): raise ValueError("Finalización inválida")
        if data["generated"] and detail["finish_reason"] in ("length", "content_filter", "tool_calls"): raise ValueError("Respuesta incompleta")
    if data["generated"] and data.get("reason", "answered") != "answered": raise ValueError("Respuesta incompatible")
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
        answer_mode = payload.get("answer_mode", "brief")
        if answer_mode not in ("brief", "expanded"):
            return jsonify(type="error", code="invalid"), 400
        value = value.strip()
        start = perf_counter()
        if mode == "rag":
            endpoint = os.getenv("GLF_RAG_URL", "")
            parsed = urlsplit(endpoint)
            if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".hf.space") or parsed.username or parsed.password:
                return jsonify(error="El servicio RAG necesita atención del administrador. Puede utilizar la búsqueda local."), 503
            try:
                response = post(endpoint, json={"query": value, "answer_mode": answer_mode}, headers={"X-Demo-Key": os.getenv("GLF_RAG_KEY", "")},
                                timeout=55, allow_redirects=False)
                response.raise_for_status()
                result = validate_remote(response.json())
                return jsonify(result)
            except (requests.RequestException, ValueError, KeyError, TypeError):
                return jsonify(error="El servicio RAG no respondió con evidencia válida. Intente más tarde."), 502
        if index is None:
            return jsonify(error="Los documentos locales no están disponibles. Solicite al administrador preparar el corpus."), 503
        rows = index.search(value, 5)
        return jsonify({"generated": False, "answer": "Pasajes recuperados para revisión. Esta búsqueda local no genera una respuesta con IA.",
                        "results": rows, "sources": [], "mode": "local_retrieval",
                        "timings": {"total_seconds": perf_counter()-start}})

    @app.post("/api/query-stream")
    def query_stream():
        payload = request.get_json(silent=True)
        value = payload.get("query") if isinstance(payload, dict) else None
        mode = payload.get("mode") if isinstance(payload, dict) else None
        request_id = str(uuid4())
        if not isinstance(value, str) or not 3 <= len(value.strip()) <= 600 or mode not in ["local", "rag"]:
            return jsonify(type="error", code="invalid", request_id=request_id), 400
        answer_mode = payload.get("answer_mode", "brief")
        if answer_mode not in ("brief", "expanded"):
            return jsonify(type="error", code="invalid"), 400
        value = value.strip()
        @stream_with_context
        def events():
            started = perf_counter()
            def event(data):
                return json.dumps({**data, "request_id": request_id}, ensure_ascii=False) + "\n"
            try:
                if mode == "local":
                    yield event({"type":"stage", "stage":"retrieval", "model":"BM25 local · sin generación"})
                    response = app.make_response(query())
                    if response.status_code != 200:
                        yield event({"type":"error", "code":"configuration"}); return
                    result = response.get_json()
                    result["model"] = "BM25 local"
                else:
                    endpoint = os.getenv("GLF_RAG_URL", "")
                    parsed = urlsplit(endpoint)
                    if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".hf.space") or parsed.username or parsed.password or parsed.port or parsed.path != "/api/ask" or parsed.query or parsed.fragment or not os.getenv("GLF_RAG_KEY"):
                        yield event({"type":"error", "code":"configuration"}); return
                    yield event({"type":"stage", "stage":"connecting", "model":"BM25 + Qwen · Hugging Face"})
                    remote = post(endpoint + "-stream", json={"query": value, "answer_mode": answer_mode}, headers={"X-Demo-Key": os.environ["GLF_RAG_KEY"]}, timeout=(10,65), allow_redirects=False, stream=True)
                    try:
                        if remote.status_code != 200:
                            yield event({"type":"error", "code":"quota" if remote.status_code == 429 else "configuration" if remote.status_code in [401,403] else "unavailable"}); return
                        result = None; size = 0
                        for line in remote.iter_lines():
                            size += len(line)
                            if size > 220000 or perf_counter()-started > 70: raise ValueError("Invalid stream")
                            if not line: continue
                            item = json.loads(line)
                            if not isinstance(item, dict): raise ValueError("Invalid event")
                            kind = item.get("type")
                            if kind == "stage":
                                if item.get("stage") not in ["retrieval","context","generation","verification"] or not isinstance(item.get("model"),str) or len(item["model"])>150: raise ValueError("Invalid stage")
                                yield event({"type":"stage","stage":item["stage"],"model":item["model"]})
                            elif kind == "result":
                                result = validate_remote(item.get("result"))
                                if result.get("answer_mode", answer_mode) != answer_mode: raise ValueError("Incompatible mode")
                                break
                            elif kind == "error":
                                yield event({"type":"error","code":item.get("code") if item.get("code") in ["quota","configuration"] else "unavailable"}); return
                            elif kind != "heartbeat": raise ValueError("Invalid event")
                        if result is None: raise ValueError("Incomplete response")
                    finally: remote.close()
                result.update(query=value, request_id=request_id, mode=mode, elapsed_seconds=perf_counter()-started)
                yield event({"type":"result", "result": result})
            except requests.Timeout:
                yield event({"type":"error", "code":"timeout"})
            except requests.RequestException:
                yield event({"type":"error", "code":"unavailable"})
            except (ValueError, KeyError, TypeError):
                yield event({"type":"error", "code":"invalid-response"})
        return Response(events(), mimetype="application/x-ndjson")

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'"
        return response
    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8766, debug=False)
