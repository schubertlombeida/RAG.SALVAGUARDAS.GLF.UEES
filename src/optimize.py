"""Reproducible retrieval sensitivity, independent labels, untouched final test."""
import argparse
import csv
from itertools import product
from pathlib import Path
from statistics import mean
from .evaluate import evaluate, validate_gold
from .model import HeadingBM25
from .utils import ROOT, digest, read_jsonl, save_json

GRID = {"k1": [0.8, 1.2, 1.5], "b": [0.2, 0.75], "heading_weight": [0.0, 0.3]}


def optimize(records, development, validation, corpus_hash, grid=None):
    """Select on validation; all per-query runs retained. Never accepts a test set."""
    known = {r["chunk_id"] for r in records}
    validate_gold(development, known, corpus_hash, "development")
    validate_gold(validation, known, corpus_hash, "validation")
    if {q["query_id"] for q in development} & {q["query_id"] for q in validation}:
        raise ValueError("Fuga de datos: IDs repetidos")
    normalize = lambda q: " ".join(q["query"].casefold().split())
    if {normalize(q) for q in development} & {normalize(q) for q in validation}:
        raise ValueError("Fuga de datos: preguntas repetidas")
    groups_a = {q.get("intent_group") for q in development if q.get("intent_group")}
    groups_b = {q.get("intent_group") for q in validation if q.get("intent_group")}
    if groups_a & groups_b: raise ValueError("Fuga de datos: intención compartida")
    if not all(any(q["answerable"] for q in group) for group in (development, validation)):
        raise ValueError("Se requieren preguntas contestables en ambas particiones")
    grid = grid or GRID
    runs = []
    for values in product(*(grid[k] for k in GRID)):
        params = dict(zip(GRID, values))
        index = HeadingBM25(records, **params)
        runs.append({"parameters":params, "development":evaluate(index, development, corpus_hash,"development"),
                     "validation":evaluate(index, validation, corpus_hash,"validation")})
    best = max(runs, key=lambda r: (r["validation"]["overall"]["metrics"]["recall_at_5"], r["validation"]["overall"]["metrics"]["mrr_at_5"], -r["parameters"]["heading_weight"]))
    marginals = []
    for key, values in grid.items():
        for value in values:
            scores = [r["validation"]["overall"]["metrics"]["recall_at_5"] for r in runs if r["parameters"][key] == value]
            marginals.append({"parameter":key,"value":value,"mean_validation_recall_at_5":mean(scores)})
    importance = {key:max(r["mean_validation_recall_at_5"] for r in marginals if r["parameter"]==key)-min(r["mean_validation_recall_at_5"] for r in marginals if r["parameter"]==key) for key in grid}
    interactions = [{"k1":k1,"heading_weight":weight,"mean_validation_recall_at_5":mean(r["validation"]["overall"]["metrics"]["recall_at_5"] for r in runs if r["parameters"]["k1"]==k1 and r["parameters"]["heading_weight"]==weight)} for k1,weight in product(grid["k1"],grid["heading_weight"])]
    return {"corpus_sha256":corpus_hash,"grid":grid,"selection_metric":"validation Recall@5, then MRR@5, then lower heading weight", "test_used":False,
            "selected_parameters":best["parameters"], "runs":runs,"marginals":marginals,"importance":importance,"interactions":interactions,
            "interpretation":"Sensitivity of retrieval parameters on validation; not causal importance or Qwen weight training."}


def save_report(report, output):
    output = Path(output)
    if output.exists(): raise ValueError("Use una carpeta nueva; no sobrescriba resultados")
    output.mkdir(parents=True)
    save_json(output/"optimization.json",report)
    for name in ("marginals","interactions"):
        rows = report[name]
        with (output/f"{name}.csv").open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes=plt.subplots(1,3,figsize=(11,3.6),constrained_layout=True)
    for axis,parameter in zip(axes,report["grid"]):
        values=[r for r in report["marginals"] if r["parameter"]==parameter]
        axis.plot([r["value"] for r in values],[r["mean_validation_recall_at_5"] for r in values],marker="o",color="#008a99")
        axis.set(title=parameter,ylabel="Recall@5 validación",ylim=(0,1));axis.grid(alpha=.2)
    fig.savefig(output/"sensitivity.png",dpi=170);plt.close(fig)
    fig,axis=plt.subplots(figsize=(7,4),constrained_layout=True)
    axis.bar(report["importance"].keys(),report["importance"].values(),color=["#008a99","#193866","#d48d22"])
    axis.set(ylabel="Rango marginal de Recall@5",title="Importancia dentro de los rangos probados")
    fig.savefig(output/"importance.png",dpi=170);plt.close(fig)
    fig,axis=plt.subplots(figsize=(6,4),constrained_layout=True)
    matrix=[[next(r["mean_validation_recall_at_5"] for r in report["interactions"] if r["k1"]==k and r["heading_weight"]==w) for w in report["grid"]["heading_weight"]] for k in report["grid"]["k1"]]
    im=axis.imshow(matrix,vmin=0,vmax=1,cmap="viridis",aspect="auto")
    axis.set(xticks=range(len(report["grid"]["heading_weight"])),xticklabels=report["grid"]["heading_weight"],yticks=range(len(report["grid"]["k1"])),yticklabels=report["grid"]["k1"],xlabel="Peso de encabezados",ylabel="k1",title="Interacción: Recall@5 medio de validación")
    fig.colorbar(im,ax=axis);fig.savefig(output/"interaction.png",dpi=170);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus",default=str(ROOT/"data/processed/chunks.jsonl"))
    parser.add_argument("--development",required=True);parser.add_argument("--validation",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    report=optimize(read_jsonl(args.corpus),read_jsonl(args.development),read_jsonl(args.validation),digest(Path(args.corpus)))
    save_report(report,args.output)

if __name__=="__main__": main()
