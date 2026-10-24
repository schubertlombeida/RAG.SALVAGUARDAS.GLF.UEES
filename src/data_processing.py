"""Corpus público con páginas y versiones verificables."""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import requests
from pypdf import PdfReader
from .utils import ROOT, save_json

def chunk_page(text, document_id, page, source_name, source_url, target=1200, overlap=180):
    if target <= overlap or overlap < 0:
        raise ValueError("Tamaño y solapamiento incompatibles")
    clean = re.sub(r"[ \t]+", " ", (text or "").replace("\x00", " ")).strip()
    rows, start = [], 0
    while start < len(clean):
        end = min(start + target, len(clean))
        if end < len(clean):
            boundary = clean.rfind(" ", start + int(target * .65), end)
            if boundary > start:
                end = boundary
        fragment = clean[start:end].strip()
        if fragment:
            rows.append({"chunk_id": f"{document_id}::P{page:02d}C{len(rows)+1:02d}",
                         "document_id": document_id, "page": page, "source_name": source_name,
                         "source_url": source_url, "language": "es", "text": fragment})
        if end == len(clean):
            break
        start = max(start + 1, end - overlap)
    return rows

def validate_records(records):
    if not records:
        raise ValueError("Corpus vacío")
    ids = [row["chunk_id"] for row in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Identificadores duplicados")
    for row in records:
        if not row.get("text", "").strip() or not isinstance(row.get("page"), int) or row["page"] < 1:
            raise ValueError("Fragmento sin texto o página válida")
        url = urlsplit(row["source_url"])
        if url.scheme != "https" or url.hostname != "galapagoslifefund.org.ec":
            raise ValueError("Fuente fuera del dominio público permitido")
    return records

def prepare(output=None):
    folder = Path(output or ROOT / "data")
    records, manifest = [], []
    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    for source in sources:
        url = urlsplit(source["url"])
        if url.scheme != "https" or url.hostname != "galapagoslifefund.org.ec":
            raise ValueError("URL no permitida")
        response = requests.get(source["url"], timeout=(15, 60), allow_redirects=False,
                                headers={"User-Agent": "GLF-UEES-Academic-Reproducibility/1.0"})
        response.raise_for_status()
        content = response.content
        if not content.startswith(b"%PDF") or len(content) > 20 * 1024 * 1024:
            raise ValueError("PDF inválido o demasiado grande")
        pdf = PdfReader(io.BytesIO(content))
        for page_number, page in enumerate(pdf.pages, 1):
            records.extend(chunk_page(page.extract_text() or "", source["document_id"], page_number,
                                      source["name"], source["url"]))
        manifest.append(dict(source, sha256=hashlib.sha256(content).hexdigest(),
                             bytes=len(content), pages=len(pdf.pages)))
        raw = folder / "raw" / (source["document_id"] + ".pdf")
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(content)
    validate_records(records)
    target = folder / "processed/chunks.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    save_json(ROOT / "results/metrics/public_sources_manifest.json", manifest)
    return records

if __name__ == "__main__":
    print(f"Fragmentos preparados: {len(prepare())}")
