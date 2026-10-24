"""Metrics from independent human annotations; never uses Qwen as its own judge."""
import argparse
import statistics
import math
from .evaluate import validate_gold, wilson
from .utils import read_jsonl, save_json


def summarize_answers(labels, runs, reviews, corpus_hash, known_ids, split="test"):
    validate_gold(labels, known_ids, corpus_hash, split)
    questions = {q["query_id"]: q for q in labels}
    run_map = {}
    for run in runs:
        key = (run["configuration"], run["query_id"])
        if key in run_map or run["query_id"] not in questions or run.get("corpus_sha256") != corpus_hash or type(run.get("generated")) is not bool:
            raise ValueError("Ejecución duplicada, sin pregunta o incompatible con el corpus")
        run_map[key] = run
    grouped, seen = {}, set()
    for review in reviews:
        key = (review["configuration"], review["query_id"])
        if key in seen or key not in run_map: raise ValueError("Revisión duplicada o sin ejecución")
        seen.add(key)
        question, run = questions[key[1]], run_map[key]
        if review.get("review_status") != "approved" or not str(review.get("reviewer", "")).strip() or review["reviewer"] == question["question_author"] or not review.get("review_date"):
            raise ValueError("Se requiere revisión humana independiente")
        total, supported = review.get("claims_total"), review.get("claims_supported")
        if type(total) is not int or type(supported) is not int or not 0 <= supported <= total or (not run["generated"] and total != 0):
            raise ValueError("Conteos de afirmaciones inválidos")
        if run["generated"] and total < 1: raise ValueError("Anote las afirmaciones de cada respuesta generada")
        if type(review.get("answer_adequate")) is not bool or not review.get("review_note", "").strip():
            raise ValueError("Falta juicio de utilidad y justificación")
        for field in ("manual_seconds", "assisted_seconds"):
            value=review.get(field)
            if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or value <= 0): raise ValueError("Tiempo inválido")
        grouped.setdefault(key[0],[]).append((question,run,review))
    output={}
    for configuration, rows in grouped.items():
        answerable=[r for r in rows if r[0]["answerable"]]
        unanswerable=[r for r in rows if not r[0]["answerable"]]
        correct=sum(not r[1]["generated"] for r in unanswerable)
        wrong=sum(not r[1]["generated"] for r in answerable)
        useful=sum(r[2]["answer_adequate"] for r in rows)
        total=sum(r[2]["claims_total"] for r in rows);supported=sum(r[2]["claims_supported"] for r in rows)
        timed=[r[2] for r in rows if r[2].get("manual_seconds") and r[2].get("assisted_seconds")]
        output[configuration]={"reviewed_answers":len(rows),"adequate_answers":useful,"adequacy_wilson95":wilson(useful,len(rows)),
            "claims_total":total,"claims_supported":supported,"claim_support_fraction":supported/total if total else None,
            "unanswerable_questions":len(unanswerable),"correct_abstentions":correct,"correct_abstention_wilson95":wilson(correct,len(unanswerable)) if unanswerable else None,
            "answerable_questions":len(answerable),"wrong_abstentions":wrong,"wrong_abstention_wilson95":wilson(wrong,len(answerable)) if answerable else None,
            "paired_timing_cases":len(timed),"median_manual_seconds":statistics.median(r["manual_seconds"] for r in timed) if timed else None,
            "median_assisted_seconds":statistics.median(r["assisted_seconds"] for r in timed) if timed else None,
            "median_paired_saving_seconds":statistics.median(r["manual_seconds"]-r["assisted_seconds"] for r in timed) if timed else None}
    return {"corpus_sha256":corpus_hash,"split":split,"configurations":output,
            "unreviewed_runs":len(run_map)-len(seen),"note":"Claims within an answer are correlated: no Wilson interval is assigned to the pooled claim fraction. Timings must include citation verification."}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ("labels","runs","reviews","corpus","output"): parser.add_argument("--"+flag,required=True)
    args=parser.parse_args()
    from pathlib import Path
    from .utils import digest
    target=Path(args.output)
    if target.exists(): parser.error("Use un archivo nuevo; no sobrescriba resultados")
    result=summarize_answers(read_jsonl(args.labels),read_jsonl(args.runs),read_jsonl(args.reviews),digest(Path(args.corpus)),{r["chunk_id"] for r in read_jsonl(args.corpus)})
    save_json(target,result)
