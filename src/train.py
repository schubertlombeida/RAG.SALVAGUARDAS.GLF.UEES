"""Construir el índice RAG; no entrena ni ajusta un modelo de lenguaje."""
from .utils import ROOT, digest, read_jsonl, save_json
from .model import BM25

def build():
    path = ROOT / "data/processed/chunks.jsonl"
    index = BM25(read_jsonl(path))
    config = {"method": index.name, "k1": index.k1, "b": index.b, "top_k": 5,
              "corpus_sha256": digest(path), "chunks": len(index.records), "fit_llm": False}
    save_json(ROOT / "models/index_config.json", config)
    return config

if __name__ == "__main__":
    print(build())
