from __future__ import annotations

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path("/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws")
OUTPUT_DIR = ROOT / "outputs"


mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


TEAL = "#0f766e"
TEAL_FILL = "#e6f4f1"
BORDER = "#4b5563"
LIGHT_FILL = "#f7f7f7"
TEXT = "#111827"
SUBTEXT = "#374151"


def add_round_box(ax, x, y, w, h, facecolor, edgecolor, lw=1.7, radius=0.02):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.006,rounding_size={radius}",
        linewidth=lw,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    return patch


def add_stage(ax, x, y, w, h, title, lines, highlight=False):
    face = TEAL_FILL if highlight else LIGHT_FILL
    edge = TEAL if highlight else BORDER
    add_round_box(ax, x, y, w, h, face, edge, lw=2.0 if highlight else 1.6, radius=0.018)

    ax.text(
        x + 0.015,
        y + h - 0.035,
        title,
        ha="left",
        va="top",
        fontsize=9.2,
        fontweight="bold",
        color=TEXT,
    )

    current_y = y + h - 0.085
    for line in lines:
        indent = 0.0
        bullet = "•"
        color = SUBTEXT
        if line.startswith("__sub__"):
            line = line.replace("__sub__", "", 1)
            indent = 0.018
            bullet = ""
            color = TEXT

        text = f"{bullet} {line}" if bullet else line
        ax.text(
            x + 0.018 + indent,
            current_y,
            text,
            ha="left",
            va="top",
            fontsize=7.2,
            color=color,
            wrap=True,
        )
        current_y -= 0.045

    return (x, y, w, h)


def add_arrow(ax, left_box, right_box):
    x1 = left_box[0] + left_box[2]
    y1 = left_box[1] + left_box[3] / 2
    x2 = right_box[0]
    y2 = right_box[1] + right_box[3] / 2
    arrow = FancyArrowPatch(
        (x1 + 0.004, y1),
        (x2 - 0.004, y2),
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.8,
        color=BORDER,
    )
    ax.add_patch(arrow)


def build_figure():
    fig, ax = plt.subplots(figsize=(18, 5.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.95,
        "Study Pipeline: What Do Cross-Language Clone Detectors Really Learn?",
        ha="center",
        va="top",
        fontsize=12.5,
        fontweight="bold",
        color=TEXT,
    )

    w = 0.145
    h = 0.56
    y = 0.27
    xs = [0.02, 0.18, 0.34, 0.50, 0.66, 0.82]

    boxes = []
    boxes.append(
        add_stage(
            ax,
            xs[0],
            y,
            w,
            h,
            "1. Dataset Construction",
            [
                "CodeNet-derived Java-X dataset",
                "clone / non-clone pairs",
                "problem IDs + language pairs",
            ],
        )
    )
    boxes.append(
        add_stage(
            ax,
            xs[1],
            y,
            w,
            h,
            "2. Evaluation Protocols",
            [
                "P0: Pair-random split",
                "__sub__(possible leakage)",
                "P1: Code-disjoint split",
                "P2: Problem-disjoint split",
                "P3: Held-out language transfer",
            ],
        )
    )
    boxes.append(
        add_stage(
            ax,
            xs[2],
            y,
            w,
            h,
            "3. Shortcut &\nDependency Audit",
            [
                "A1-A4 shortcut baselines",
                "A4-full shallow feature model",
                "Partner shuffling (B1-B3)",
            ],
        )
    )
    boxes.append(
        add_stage(
            ax,
            xs[3],
            y - 0.01,
            w,
            h + 0.02,
            "4. Semantic\nCounterfactual Evaluation",
            [
                "semantic-preserving edits",
                "__sub__invariance test",
                "semantic-breaking edits",
                "__sub__sensitivity test",
            ],
            highlight=True,
        )
    )
    boxes.append(
        add_stage(
            ax,
            xs[4],
            y,
            w,
            h,
            "5. Model Behavior\nAnalysis",
            [
                "GraphCodeBERT",
                "UniXcoder",
                "embedding + SVM",
                "DeepSeek-v4-flash",
                "A4-full non-semantic baseline",
            ],
        )
    )
    boxes.append(
        add_stage(
            ax,
            xs[5],
            y,
            w,
            h,
            "6. Metrics Output",
            [
                "F1 / Balanced Accuracy / AUROC",
                "CPA / SSR / CDFR",
                "preserving consistency",
                "breaking rejection rate",
            ],
        )
    )

    for left, right in zip(boxes[:-1], boxes[1:]):
        add_arrow(ax, left, right)

    ax.text(
        xs[3] + w / 2,
        y + h + 0.06,
        "Key conceptual contribution",
        ha="center",
        va="bottom",
        fontsize=7.5,
        fontweight="bold",
        color=TEAL,
    )

    footer_x = 0.06
    footer_y = 0.08
    footer_w = 0.88
    footer_h = 0.10
    add_round_box(ax, footer_x, footer_y, footer_w, footer_h, "#ffffff", "#9ca3af", lw=1.2, radius=0.015)
    footer_text = (
        r"$\bf{Interpretation:}$ "
        r"Benchmark\ performance $\neq$ semantic\ understanding"
        "\n"
        "Protocol design affects measured results   |   "
        "Shortcut signals remain even in clean splits   |   "
        "Semantic invariance and semantic sensitivity are orthogonal"
    )
    ax.text(
        0.5,
        footer_y + footer_h / 2,
        footer_text,
        ha="center",
        va="center",
        fontsize=7.4,
        color=TEXT,
        linespacing=1.25,
    )

    return fig


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    stem = OUTPUT_DIR / "study_pipeline_figure_20260701"
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
