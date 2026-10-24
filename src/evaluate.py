"""Métricas auditables que rechazan etiquetas sin revisión independiente."""
import argparse
import math
import os
from collections import defaultdict
from .utils import ROOT, digest, read_jsonl, save_json
from .model import BM25, E5Endpoint

def wilson(successes, n, z=1.96):
    if not 0 <= successes <= n or n <= 0:
        raise ValueError("Conteos inválidos")
    p = successes / n
    center = (p + z*z/(2*n)) / (1+z*z/n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    return [center-half, center+half]

def retrieval_metrics(ranked, relevant, k=5):
    if k < 1:
        raise ValueError("k inválido")
    ranked = list(dict.fromkeys(ranked))[:k]
    relevant = set(relevant)
    if not relevant:
        return {"hit_at_5": None, "recall_at_5": None, "precision_at_5": None, "mrr_at_5": None}
    hits = len(set(ranked) & relevant)
    first = next((1/r for r, cid in enumerate(ranked, 1) if cid in relevant), 0)
    return {"hit_at_5": int(hits > 0), "recall_at_5": hits/len(relevant),
            "precision_at_5": hits/k, "mrr_at_5": first}

def validate_gold(queries, known_ids, expected_hash, split):
    if not queries or split not in ("development", "validation", "test"):
        raise ValueError("Preguntas o partición inválidas")
    ids = set()
    for q in queries:
        required = ["query_id", "query", "theme", "reviewer", "review_date", "question_author"]
        if any(not str(q.get(key, "")).strip() for key in required):
            raise ValueError("Falta autoría o anotación verificable")
        if q["query_id"] in ids:
            raise ValueError("ID de pregunta duplicado")
        ids.add(q["query_id"])
        if q.get("review_status") != "approved" or q["reviewer"] == q["question_author"]:
            raise ValueError("Se requiere revisor independiente y aprobación explícita")
        if q.get("split") != split or q.get("corpus_sha256") != expected_hash:
            raise ValueError("Partición o versión del corpus incompatible")
        gold = q.get("relevant_chunk_ids")
        if not isinstance(gold, list) or len(gold) != len(set(gold)) or not set(gold) <= known_ids:
            raise ValueError("Pasajes relevantes inválidos")
        if type(q.get("answerable")) is not bool or q["answerable"] != bool(gold):
            raise ValueError("Contestabilidad incompatible con los pasajes")
        if not q.get("annotation_note", "").strip():
            raise ValueError("Documente el pasaje correcto o la razón de ausencia")

def evaluate(index, queries, corpus_hash, split="test"):
    validate_gold(queries, {r["chunk_id"] for r in index.records}, corpus_hash, split)
    rows = []
    for query in queries:
        ranked = [r["chunk_id"] for r in index.search(query["query"], 5)]
        rows.append(dict(query_id=query["query_id"], theme=query["theme"],
                         answerable=query["answerable"], retrieved=ranked,
                         **retrieval_metrics(ranked, query["relevant_chunk_ids"])))
    def summarize(group):
        valid = [r for r in group if r["answerable"]]
        if not valid:
            return {"answerable_questions": 0, "metrics": None}
        hits = sum(r["hit_at_5"] for r in valid)
        return {"answerable_questions": len(valid), "hits": hits, "hit_at_5_wilson95": wilson(hits, len(valid)),
                "metrics": {key: sum(r[key] for r in valid)/len(valid) for key in
                            ["hit_at_5", "recall_at_5", "precision_at_5", "mrr_at_5"]}}
    themes = defaultdict(list)
    for row in rows:
        themes[row["theme"]].append(row)
    return {"method": index.name, "split": split, "corpus_sha256": corpus_hash,
            "questions": len(rows), "overall": summarize(rows),
            "by_theme": {theme: summarize(group) for theme, group in themes.items()},
            "unanswerable_questions": sum(not r["answerable"] for r in rows),
            "abstention_quality": None, "note": "Recuperación sola no mide abstención ni soporte de afirmaciones.",
            "per_query": rows}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True)
    parser.add_argument("--split", choices=["development", "validation", "test"], default="test")
    parser.add_argument("--method", choices=["bm25", "e5"], default="bm25")
    args = parser.parse_args()
    corpus = ROOT / "data/processed/chunks.jsonl"
    records, labels, corpus_hash = read_jsonl(corpus), read_jsonl(args.labels), digest(corpus)
    # Validate annotations before making any paid or authenticated inference request.
    validate_gold(labels, {r["chunk_id"] for r in records}, corpus_hash, args.split)
    if args.method == "e5":
        endpoint, key = os.getenv("GLF_E5_ENDPOINT"), os.getenv("GLF_E5_API_KEY")
        if not endpoint or not key:
            parser.error("Configure GLF_E5_ENDPOINT y GLF_E5_API_KEY en el servidor")
        index = E5Endpoint(records, endpoint, key)
    else:
        index = BM25(records)
    report = evaluate(index, labels, corpus_hash, args.split)
    save_json(ROOT / f"results/metrics/human_{args.method}_{args.split}.json", report)
