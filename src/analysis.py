"""EDA público y visualización de antecedentes sin inventar resultados."""
import csv
import json
from collections import Counter, defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from .utils import ROOT, read_jsonl, save_json

plt.rcParams.update({"font.family": "Arial", "font.size": 11, "text.color": "black",
                     "axes.labelcolor": "black", "axes.titleweight": "bold", "axes.titlesize": 12})
FIGURES = ROOT / "results/figures"
# Keep document and parameter colors consistent across their related charts.
PALETTE = ["#0072B2", "#009E73", "#56B4E9", "#E69F00", "#CC79A7", "#D55E00", "#008B8B"]

def save(fig, filename):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def eda():
    rows = read_jsonl(ROOT / "data/processed/chunks.jsonl")
    sources = json.loads((ROOT / "results/metrics/public_sources_manifest.json").read_text(encoding="utf-8"))
    docs = {s["document_id"]: s for s in sources}
    names = [s["name"].replace(" - ", "\n") for s in sources]
    counts = Counter(r["document_id"] for r in rows)
    lengths = [len(r["text"]) for r in rows]
    word_counts = [len(r["text"].split()) for r in rows]
    by_doc = [[len(r["text"].split()) for r in rows if r["document_id"] == s["document_id"]] for s in sources]
    fields = ["chunk_id", "document_id", "page", "source_name", "source_url", "text"]
    complete = {field: sum(bool(r.get(field)) for r in rows) for field in fields}
    page_lengths = []
    from pypdf import PdfReader
    empty_pages = 0
    for source in sources:
        for page in PdfReader(ROOT / "data/raw" / (source["document_id"]+".pdf")).pages:
            n = len((page.extract_text() or "").strip())
            page_lengths.append(n)
            empty_pages += int(n == 0)
    report = {"documents": len(sources), "pages": sum(s["pages"] for s in sources), "chunks": len(rows),
              "chunks_by_document": dict(counts), "empty_pages": empty_pages,
              "exact_duplicate_texts": len(rows)-len({r["text"] for r in rows}),
              "characters_min_median_max": [min(lengths), float(np.median(lengths)), max(lengths)],
              "words_min_median_max": [min(word_counts), float(np.median(word_counts)), max(word_counts)],
              "complete_metadata": complete, "scope": "Corpus público reconstruido; sin etiquetas de relevancia"}
    save_json(ROOT / "results/metrics/public_eda.json", report)
    document_colors = [PALETTE[i % len(PALETTE)] for i in range(len(sources))]
    fig, ax = plt.subplots(figsize=(9, 4.2)); ax.barh(names, [counts[s["document_id"]] for s in sources], color=document_colors)
    ax.set_title("Fragmentos por documento público"); ax.set_xlabel("Fragmentos"); save(fig, "01_chunks_by_document.png")
    fig, ax = plt.subplots(figsize=(9, 4.2)); ax.barh(names, [s["pages"] for s in sources], color=document_colors)
    ax.set_title("Páginas por documento público"); ax.set_xlabel("Páginas"); save(fig, "02_pages_by_document.png")
    fig, ax = plt.subplots(figsize=(8, 3.5)); ax.hist(lengths, bins=20, color=PALETTE[0], edgecolor="white")
    ax.set_title("Longitud de los fragmentos"); ax.set_xlabel("Caracteres"); ax.set_ylabel("Frecuencia"); save(fig, "03_chunk_lengths.png")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    boxes = ax.boxplot(by_doc, tick_labels=names, vert=False, patch_artist=True, medianprops={"color": "black"})
    for box, color in zip(boxes["boxes"], document_colors):
        box.set_facecolor(color)
    ax.set_title("Palabras por fragmento y documento"); ax.set_xlabel("Palabras"); save(fig, "04_words_by_document.png")
    fig, ax = plt.subplots(figsize=(8, 3.5)); ax.hist(page_lengths, bins=20, color=PALETTE[1], edgecolor="white")
    ax.set_title("Texto extraído por página"); ax.set_xlabel("Caracteres"); ax.set_ylabel("Páginas"); save(fig, "05_page_text_lengths.png")
    fig, ax = plt.subplots(figsize=(8, 3.5)); ax.bar(fields, list(complete.values()), color=PALETTE[1]); ax.set_ylim(0, len(rows)*1.12)
    ax.set_title("Completitud de metadatos"); ax.set_ylabel("Fragmentos con dato"); save(fig, "06_metadata_completeness.png")
    return report

def historical_plots():
    folder = ROOT / "results/metrics/historical"
    def read(name):
        with (folder/name).open(encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    marginal = read("partial_dependence_marginal.csv")
    parameters = list(dict.fromkeys(row["parameter"] for row in marginal))
    parameter_colors = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(parameters)}
    fig, axes = plt.subplots(2, 2, figsize=(9, 6))
    for name, ax in zip(parameters, axes.flat):
        group = [r for r in marginal if r["parameter"] == name]
        ax.plot([float(r["value"]) for r in group], [float(r["development_recall_at_5"]) for r in group], color=parameter_colors[name], marker="o")
        ax.set_title(name); ax.set_ylabel("Recall@5 medio histórico")
    fig.suptitle("Sensibilidad histórica recibida · no reevaluada", fontsize=12, fontweight="bold")
    save(fig, "07_historical_partial_dependence.png")
    importance = read("hyperparameter_importance.csv")
    fig, ax = plt.subplots(figsize=(8, 3.5)); ax.barh([r["parameter"] for r in importance], [100*float(r["marginal_recall_span"]) for r in importance], color=[parameter_colors[r["parameter"]] for r in importance])
    ax.set_title("Importancia marginal histórica recibida"); ax.set_xlabel("Rango en puntos porcentuales"); save(fig, "08_historical_importance.png")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for filename, ax in zip(["interaction_k1_heading_weight.csv", "interaction_b_authority_boost.csv"], axes):
        values = read(filename)
        keys = list(values[0])
        xkey = keys[0]
        ykey = "heading_weight" if "heading_weight" in filename else "glf_authority_boost"
        xs = [float(row[xkey]) for row in values]
        ys = [float(key) for key in keys[1:]]
        grid = np.asarray([[float(row[key]) for row in values] for key in keys[1:]])
        image = ax.imshow(grid, cmap="viridis", origin="lower", aspect="auto")
        ax.set_xticks(range(len(xs)), xs); ax.set_yticks(range(len(ys)), ys)
        ax.set_xlabel(xkey); ax.set_ylabel(ykey)
        fig.colorbar(image, ax=ax, label="Recall@5 histórico")
    fig.suptitle("Interacciones históricas recibidas · no reevaluadas", fontsize=12, fontweight="bold")
    save(fig, "09_historical_interactions.png")
    return {"source": "Archivos históricos recibidos", "new_optimization_run": False,
            "independent_human_validation": False}


def architecture_plot():
    """Render the documented integration routes without changing their content."""
    fig, ax = plt.subplots(figsize=(9.5, 7.7))
    ax.set(xlim=(0, 10), ylim=(0, 8)); ax.axis("off")

    def box(x, y, w, h, label, fill, edge):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                   facecolor=fill, edgecolor=edge, linewidth=1.4))
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", linespacing=1.5)

    def arrow(x, y, xx, yy, color):
        ax.annotate("", xy=(xx, yy), xytext=(x, y),
                    arrowprops={"arrowstyle": "->", "color": color, "lw": 1.6})

    box(2.2, 6.9, 5.6, .75, "Especialista y portal GLF en Vercel\nConsulta y permisos de acceso", "#E5EFFA", "#19355F")
    box(.3, 4.65, 4.1, 1.45, "Ruta semántica\nE5 pequeño en CPU de Hugging Face\nVectores de 384 dimensiones\nBúsqueda del corpus en Supabase", "#E0F3EE", "#008B8B")
    box(5.6, 4.65, 4.1, 1.45, "Ruta generativa\nBM25 sobre siete PDF públicos\nQwen mediante router de Hugging Face\ny proveedor remoto", "#E5F2FA", "#0072B2")
    arrow(3.5, 6.8, 2.4, 6.2, "#008B8B"); arrow(6.5, 6.8, 7.6, 6.2, "#0072B2")
    box(2.2, 2.7, 5.6, 1.15, "Validación de contrato y presentación\nPasajes, fuentes y páginas comprobables\nRespuesta o abstención visible", "#E5EFFA", "#19355F")
    arrow(2.4, 4.5, 3.5, 3.95, "#008B8B"); arrow(7.6, 4.5, 6.5, 3.95, "#0072B2")
    box(2.2, 1, 5.6, .9, "Revisión humana de evidencia\nInterpretación y decisión del especialista", "#FFF1D6", "#B77800")
    arrow(5, 2.55, 5, 2.05, "#19355F")
    ax.text(5, .2, "E5 no alimenta la generación Qwen en la integración revisada.", ha="center", va="center")
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / "10_architecture.png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
