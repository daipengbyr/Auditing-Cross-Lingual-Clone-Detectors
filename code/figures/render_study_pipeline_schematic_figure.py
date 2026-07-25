from __future__ import annotations

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


ROOT = Path("/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws")
OUTPUT_DIR = ROOT / "outputs"


mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif", "serif"],
        "font.size": 8,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


TEAL = "#0f766e"
INK = "#111111"
GRAY = "#5f6368"
LIGHT = "#f8f8f8"
MID = "#d4d4d4"


def box(ax, x, y, w, h, title=None, edge=GRAY, face="white", lw=0.9, r=0.012):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.006,rounding_size={r}",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    if title:
        ax.text(
            x + 0.014,
            y + h - 0.025,
            title,
            ha="left",
            va="top",
            fontsize=7.7,
            fontweight="bold",
            color=INK,
        )
    return patch


def arrow(ax, start, end, color=INK, lw=0.9, rad=0.0, style="-|>"):
    arr = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=8.5,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arr)
    return arr


def document(ax, x, y, w=0.035, h=0.055, label="", edge=INK, dashed=False):
    ls = "--" if dashed else "-"
    ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor=edge, linewidth=0.8, linestyle=ls))
    fold = Polygon(
        [[x + w * 0.72, y + h], [x + w, y + h], [x + w, y + h * 0.72]],
        closed=False,
        fill=False,
        edgecolor=edge,
        linewidth=0.75,
        linestyle=ls,
    )
    ax.add_patch(fold)
    if label:
        ax.text(x + w / 2, y + h * 0.48, label, ha="center", va="center", fontsize=6.8, color=INK)


def doc_pair(ax, x, y, left="Java", right="X", w=0.035, h=0.052, gap=0.052, dashed_right=False):
    document(ax, x, y, w, h, left)
    document(ax, x + gap, y, w, h, right, dashed=dashed_right)
    arrow(ax, (x + w + 0.004, y + h / 2), (x + gap - 0.004, y + h / 2), lw=0.7, style="<|-|>")


def funnel(ax, cx, cy, scale=1.0):
    widths = [0.074, 0.055, 0.036]
    heights = [0.026, 0.022, 0.018]
    y = cy
    for width, height in zip(widths, heights):
        poly = Polygon(
            [
                [cx - width * scale / 2, y],
                [cx + width * scale / 2, y],
                [cx + width * scale * 0.36, y - height * scale],
                [cx - width * scale * 0.36, y - height * scale],
            ],
            closed=True,
            fill=False,
            edgecolor=INK,
            linewidth=0.8,
        )
        ax.add_patch(poly)
        y -= height * scale + 0.008 * scale
    arrow(ax, (cx, y + 0.003), (cx, y - 0.035 * scale), lw=0.8)


def tiny_table(ax, x, y, w=0.075, h=0.035, rows=2, cols=5):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor=INK, linewidth=0.75))
    for i in range(1, cols):
        ax.plot([x + w * i / cols, x + w * i / cols], [y, y + h], color=INK, lw=0.45)
    for j in range(1, rows):
        ax.plot([x, x + w], [y + h * j / rows, y + h * j / rows], color=INK, lw=0.45)


def simple_network(ax, x, y, s=0.045):
    pts = [
        (x, y + s * 0.75),
        (x, y + s * 0.25),
        (x + s * 0.42, y + s),
        (x + s * 0.42, y + s * 0.5),
        (x + s * 0.42, y),
        (x + s * 0.86, y + s * 0.5),
    ]
    edges = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)]
    for a, b in edges:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color=INK, lw=0.55)
    for px, py in pts:
        ax.plot(px, py, marker="o", ms=3.4, mfc="white", mec=INK, mew=0.7)


def bullet_text(ax, x, y, lines, fs=7.1, line_gap=0.030):
    for i, line in enumerate(lines):
        ax.text(x, y - i * line_gap, line, ha="left", va="top", fontsize=fs, color=INK)


def protocol_item(ax, x, y, label, text, w=0.145):
    ax.add_patch(Rectangle((x, y), w, 0.032, fill=False, edgecolor=MID, linewidth=0.60))
    ax.text(x + 0.012, y + 0.017, label, ha="left", va="center", fontsize=7.2, fontweight="bold", color=INK)
    ax.text(x + 0.045, y + 0.017, text, ha="left", va="center", fontsize=7.0, color=INK)


def badge(ax, x, y, text):
    box(ax, x, y, 0.18, 0.042, edge=TEAL, face="white", lw=0.9, r=0.02)
    ax.text(x + 0.09, y + 0.021, text, ha="center", va="center", fontsize=8.0, color=INK)


def build_figure():
    fig, ax = plt.subplots(figsize=(11.8, 8.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.965, "Study pipeline", ha="center", va="top", fontsize=11.0, fontweight="bold", color=INK)

    # Dataset layer
    box(ax, 0.30, 0.825, 0.40, 0.105, "1. Dataset construction", lw=0.9)
    doc_pair(ax, 0.325, 0.845, "Java", "X", w=0.024, h=0.036, gap=0.055)
    doc_pair(ax, 0.420, 0.845, "Java", "X", w=0.024, h=0.036, gap=0.055)
    ax.text(
        0.545,
        0.872,
        "CodeNet-derived Java-X pairs\nclone / non-clone; problem IDs",
        ha="left",
        va="center",
        fontsize=7.1,
        color=INK,
    )

    # Protocol layer
    box(ax, 0.255, 0.665, 0.49, 0.115, "2. Evaluation protocol audit", lw=0.9)
    ax.text(0.300, 0.715, "stricter splits", ha="left", va="center", fontsize=6.8, style="italic")
    funnel(ax, 0.355, 0.746, scale=0.48)
    protocol_item(ax, 0.430, 0.728, "P0", "pair-random", w=0.135)
    protocol_item(ax, 0.430, 0.694, "P1", "code-disjoint", w=0.135)
    protocol_item(ax, 0.585, 0.728, "P2", "problem-disjoint", w=0.150)
    protocol_item(ax, 0.585, 0.694, "P3", "held-out language", w=0.150)

    # Audit branches
    box(ax, 0.105, 0.420, 0.38, 0.180, "3a. Shortcut and partner-dependency audit", lw=0.9)
    document(ax, 0.130, 0.512, 0.024, 0.036)
    ax.text(0.178, 0.530, "A1-A4 shortcut baselines", ha="left", va="center", fontsize=6.9)
    tiny_table(ax, 0.127, 0.472, 0.052, 0.026)
    ax.text(0.195, 0.485, "A4-full shallow feature model", ha="left", va="center", fontsize=6.9)
    document(ax, 0.132, 0.431, 0.022, 0.033)
    document(ax, 0.185, 0.431, 0.022, 0.033)
    arrow(ax, (0.160, 0.448), (0.181, 0.448), lw=0.65, rad=0.25, style="-|>")
    arrow(ax, (0.181, 0.442), (0.160, 0.442), lw=0.65, rad=0.25, style="-|>")
    ax.text(0.225, 0.446, "B1-B3 partner shuffling", ha="left", va="center", fontsize=6.9)

    box(ax, 0.515, 0.410, 0.38, 0.195, "3b. Semantic counterfactual audit", edge=TEAL, lw=1.4)
    ax.text(0.540, 0.545, "Preserve -> invariance", ha="left", va="center", fontsize=6.25)
    doc_pair(ax, 0.540, 0.505, "", "", w=0.018, h=0.027, gap=0.046)
    arrow(ax, (0.607, 0.524), (0.656, 0.524), color=TEAL, lw=0.8)
    doc_pair(ax, 0.668, 0.505, "", "", w=0.018, h=0.027, gap=0.041)
    ax.plot([0.535, 0.875], [0.486, 0.486], color=GRAY, lw=0.55, ls=(0, (4, 3)))
    ax.text(0.540, 0.468, "Break -> sensitivity", ha="left", va="center", fontsize=6.25)
    doc_pair(ax, 0.540, 0.427, "", "", w=0.018, h=0.027, gap=0.046)
    arrow(ax, (0.607, 0.449), (0.656, 0.449), color=TEAL, lw=0.8)
    doc_pair(ax, 0.668, 0.427, "", "", w=0.018, h=0.027, gap=0.041, dashed_right=True)

    # Model behavior layer
    box(ax, 0.205, 0.255, 0.59, 0.095, "4. Model behavior analysis", lw=0.9)
    simple_network(ax, 0.245, 0.268, 0.036)
    labels = ["GraphCodeBERT", "UniXcoder", "embedding + SVM", "DeepSeek-v4-flash", "A4-full control"]
    xs = [0.355, 0.450, 0.555, 0.665, 0.760]
    for idx, (lx, label) in enumerate(zip(xs, labels)):
        ax.text(lx, 0.293, label, ha="center", va="center", fontsize=6.35)
        if idx < len(xs) - 1:
            ax.plot([lx + 0.052, lx + 0.052], [0.272, 0.322], color=GRAY, lw=0.42)

    # Metrics layer
    box(ax, 0.245, 0.095, 0.51, 0.115, "5. Metrics and findings", lw=0.9)
    document(ax, 0.270, 0.108, 0.038, 0.047)
    tiny_table(ax, 0.274, 0.118, 0.030, 0.017, rows=2, cols=3)
    metric_items = [
        (0.330, 0.145, 0.145, "F1 / Bal. Acc. / AUROC"),
        (0.490, 0.145, 0.115, "CPA / SSR / CDFR"),
        (0.620, 0.145, 0.115, "preservation consistency"),
        (0.620, 0.105, 0.115, "breaking rejection rate"),
    ]
    for mx, my, mw, metric in metric_items:
        ax.add_patch(Rectangle((mx, my), mw, 0.034, fill=False, edgecolor=MID, linewidth=0.6))
        ax.text(mx + mw / 2, my + 0.017, metric, ha="center", va="center", fontsize=5.8)

    # Main arrows
    arrow(ax, (0.50, 0.825), (0.50, 0.780), lw=0.95)
    arrow(ax, (0.50, 0.665), (0.31, 0.600), lw=0.85, rad=0.10)
    arrow(ax, (0.50, 0.665), (0.70, 0.600), lw=0.85, rad=-0.10)
    arrow(ax, (0.295, 0.420), (0.425, 0.350), lw=0.85, rad=0.03)
    arrow(ax, (0.705, 0.420), (0.585, 0.350), lw=0.85, rad=-0.03)
    arrow(ax, (0.50, 0.255), (0.50, 0.210), lw=0.95)

    # Conclusion badges
    badge(ax, 0.185, 0.025, "Protocol matters")
    badge(ax, 0.410, 0.025, "Shortcuts remain")
    badge(ax, 0.635, 0.025, "Invariance != sensitivity")
    arrow(ax, (0.36, 0.095), (0.275, 0.067), lw=0.55, style="-|>")
    arrow(ax, (0.50, 0.095), (0.50, 0.067), lw=0.55, style="-|>")
    arrow(ax, (0.64, 0.095), (0.725, 0.067), lw=0.55, style="-|>")

    return fig


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    stem = OUTPUT_DIR / "study_pipeline_schematic_figure_v5_20260701"
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=260, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
