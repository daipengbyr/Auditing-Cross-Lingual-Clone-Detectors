from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path("/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws")
OUTPUT_DIR = ROOT / "outputs"
SPLIT_DIR = OUTPUT_DIR / "third_round_remote_mirror_20260626" / "splits"


mpl.rcParams.update(
    {
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


PAIR_SPECS = {
    "p0_train": {
        "path": SPLIT_DIR / "clean_protocol_splits_p0eb_20260625" / "train.jsonl",
        "pair_id": "4c55e522b6800332",
    },
    "p0_test": {
        "path": SPLIT_DIR / "clean_protocol_splits_p0eb_20260625" / "test.jsonl",
        "pair_id": "d675a125c3031767",
    },
    "p1_rep": {
        "path": SPLIT_DIR / "clean_protocol_splits_p0eb_20260625" / "train.jsonl",
        "pair_id": "6e8c5505420fa7b8",
    },
    "p2_train": {
        "path": SPLIT_DIR / "p2" / "train.jsonl",
        "pair_id": "c2a7c3ac3f91f4db",
    },
    "p2_test": {
        "path": SPLIT_DIR / "p2" / "test.jsonl",
        "pair_id": "4f9d69cb6a94ca01",
    },
    "p3_rep": {
        "path": SPLIT_DIR / "clean_protocol_splits_p0eb_20260625" / "train.jsonl",
        "pair_id": "272e084d2ebc04fc",
    },
}


def load_pair(path: Path, pair_id: str) -> dict:
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if row["split_pair_id"] == pair_id:
                return row
    raise ValueError(f"Pair {pair_id} not found in {path}")


def shorten_code(code: str, width: int = 24, max_lines: int = 5) -> str:
    cleaned = code.replace("\t", "    ").strip()
    lines = []
    for raw_line in cleaned.splitlines():
        stripped = raw_line.rstrip()
        if not stripped:
            continue
        if stripped.startswith("//") or stripped.startswith("///"):
            continue
        stripped = stripped.encode("ascii", "ignore").decode("ascii")
        if not stripped:
            continue
        wrapped = textwrap.wrap(
            stripped,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
        lines.extend(wrapped if wrapped else [""])
        if len(lines) >= max_lines:
            break
    lines = lines[:max_lines]
    if lines:
        lines[-1] = lines[-1] + " ..."
    return "\n".join(lines)


def add_round_box(ax, xywh, fc="#ffffff", ec="#cad3df", lw=1.0, radius=0.018):
    x, y, w, h = xywh
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.01,rounding_size={radius}",
        linewidth=lw,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    return patch


def add_tag(ax, x, y, text, fc, ec=None, color="white", fs=8, weight="bold"):
    ax.text(
        x,
        y,
        text,
        va="center",
        ha="left",
        fontsize=fs,
        color=color,
        fontweight=weight,
        bbox=dict(
            boxstyle="round,pad=0.28,rounding_size=0.14",
            facecolor=fc,
            edgecolor=ec or fc,
            linewidth=0.8,
        ),
    )


def draw_code_card(ax, x, y, w, h, lang, code, tone="#f7f9fc"):
    add_round_box(ax, (x, y, w, h), fc=tone, ec="#d7dfea", lw=0.9, radius=0.016)
    ax.text(
        x + 0.012,
        y + h - 0.03,
        lang,
        ha="left",
        va="top",
        fontsize=8,
        fontweight="bold",
        color="#334155",
    )
    ax.text(
        x + 0.012,
        y + h - 0.055,
        code,
        ha="left",
        va="top",
        family="DejaVu Sans Mono",
        fontsize=5.7,
        color="#0f172a",
        linespacing=1.12,
    )


def draw_split_column(ax, x, y, w, h, title, pair, label_color):
    add_round_box(ax, (x, y, w, h), fc="#ffffff", ec="#bfc9d7", lw=1.0, radius=0.02)
    add_tag(ax, x + 0.012, y + h - 0.03, title, label_color)
    add_tag(
        ax,
        x + 0.17,
        y + h - 0.03,
        f"{pair['problem_id_1']}",
        fc="#eef2ff",
        ec="#c7d2fe",
        color="#3730a3",
        fs=7.5,
    )
    draw_code_card(
        ax,
        x + 0.018,
        y + 0.11,
        w * 0.43,
        h - 0.16,
        pair["ll1"],
        shorten_code(pair["codeA"]),
    )
    draw_code_card(
        ax,
        x + w * 0.53,
        y + 0.11,
        w * 0.43,
        h - 0.16,
        pair["ll2"],
        shorten_code(pair["codeB"]),
    )
    ax.text(
        x + 0.018,
        y + 0.055,
        "Cross-language clone pair",
        ha="left",
        va="center",
        fontsize=7.2,
        color="#475569",
    )


def draw_protocol_panel(ax, panel_label, title, subtitle):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    add_round_box(ax, (0.0, 0.0, 1.0, 1.0), fc="#ffffff", ec="#d6dde7", lw=1.2, radius=0.03)
    ax.text(0.03, 0.95, panel_label, fontsize=11, fontweight="bold", va="top", ha="left", color="#0f172a")
    ax.text(0.12, 0.95, title, fontsize=11, fontweight="bold", va="top", ha="left", color="#0f172a")
    ax.text(0.12, 0.895, subtitle, fontsize=8.2, va="top", ha="left", color="#475569")


def build_figure(pairs: dict[str, dict]) -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.2), constrained_layout=True)
    axes = axes.ravel()

    # (a) P0
    ax = axes[0]
    draw_protocol_panel(
        ax,
        "(a)",
        "P0 Pair-Random Split",
        "The same programming problem can appear in both training and test splits.",
    )
    draw_split_column(ax, 0.04, 0.16, 0.43, 0.62, "Train", pairs["p0_train"], "#0ea5e9")
    draw_split_column(ax, 0.53, 0.16, 0.43, 0.62, "Test", pairs["p0_test"], "#f97316")
    ax.annotate(
        "",
        xy=(0.53, 0.49),
        xytext=(0.47, 0.49),
        arrowprops=dict(arrowstyle="<->", color="#64748b", lw=1.2),
    )
    ax.text(0.50, 0.55, "same problem", ha="center", va="bottom", fontsize=7.8, color="#334155")
    add_tag(ax, 0.04, 0.08, "Leakage risk: shared task identity", fc="#fee2e2", ec="#fecaca", color="#991b1b", fs=7.4)

    # (b) P1
    ax = axes[1]
    draw_protocol_panel(
        ax,
        "(b)",
        "P1 Code-Disjoint Split",
        "Exact code overlap is removed, but protocol-level task cues may still remain.",
    )
    draw_split_column(ax, 0.11, 0.21, 0.78, 0.56, "Representative Pair", pairs["p1_rep"], "#14b8a6")
    add_tag(ax, 0.11, 0.11, "Constraint: no exact code overlap across splits", fc="#dcfce7", ec="#bbf7d0", color="#166534", fs=7.4)
    add_tag(ax, 0.56, 0.11, "Goal: weaken memorization by code identity", fc="#eff6ff", ec="#bfdbfe", color="#1d4ed8", fs=7.4)

    # (c) P2
    ax = axes[2]
    draw_protocol_panel(
        ax,
        "(c)",
        "P2 Problem-Disjoint Split",
        "Train and test are separated by programming problem, blocking direct task reuse.",
    )
    draw_split_column(ax, 0.04, 0.16, 0.43, 0.62, "Train", pairs["p2_train"], "#0ea5e9")
    draw_split_column(ax, 0.53, 0.16, 0.43, 0.62, "Test", pairs["p2_test"], "#f97316")
    ax.text(0.50, 0.55, "different problems", ha="center", va="bottom", fontsize=7.8, color="#334155")
    ax.annotate(
        "",
        xy=(0.53, 0.49),
        xytext=(0.47, 0.49),
        arrowprops=dict(arrowstyle="<->", color="#64748b", lw=1.2, linestyle="--"),
    )
    add_tag(ax, 0.04, 0.08, "Audit target: problem overlap = 0", fc="#ede9fe", ec="#ddd6fe", color="#5b21b6", fs=7.4)

    # (d) P3
    ax = axes[3]
    draw_protocol_panel(
        ax,
        "(d)",
        "P3 Held-Out-Language Problem-Disjoint Split",
        "The target language is absent from training, so performance reflects transfer under stricter isolation.",
    )
    add_round_box(ax, (0.05, 0.20, 0.39, 0.58), fc="#ffffff", ec="#bfc9d7", lw=1.0, radius=0.02)
    add_tag(ax, 0.07, 0.74, "Train", "#0ea5e9")
    ax.text(0.07, 0.67, "Allowed language pairs", fontsize=8, fontweight="bold", color="#334155", ha="left")
    for idx, label in enumerate(["Java→C++", "Java→Go", "Java→Python", "Java→C#", "… (no Rust)"]):
        ax.text(0.09, 0.60 - idx * 0.085, f"• {label}", fontsize=8.2, color="#0f172a", ha="left", va="center")
    add_tag(ax, 0.07, 0.25, "Constraint: held-out target language", fc="#dcfce7", ec="#bbf7d0", color="#166534", fs=7.2)

    draw_split_column(ax, 0.50, 0.20, 0.45, 0.58, "Test", pairs["p3_rep"], "#f97316")
    add_tag(ax, 0.50, 0.11, "Audit targets: problem overlap = 0; target language unseen in train", fc="#ede9fe", ec="#ddd6fe", color="#5b21b6", fs=7.2)

    return fig


def write_caption_note(output_dir: Path) -> None:
    note = """Figure suggestion for Section 2.2

Caption:
Illustrative examples of the four evaluation protocols used in this study. (a) P0 (Pair-Random Split) permits weak task isolation, so solutions to the same programming problem may appear in both training and test splits. (b) P1 (Code-Disjoint Split) removes exact code overlap across splits. (c) P2 (Problem-Disjoint Split) further prevents any programming problem from appearing in more than one split. (d) P3 (Held-Out-Language Problem-Disjoint Split) additionally evaluates transfer to a target language that is absent from training. The snippets are representative examples used to visualize protocol semantics rather than to summarize the full dataset distribution.

Suggested in-text reference:
Figure~\\ref{fig:protocol_schematic} visualizes the four evaluation protocols with representative Java-to-X clone pairs and highlights the leakage channel that each protocol is designed to remove.
"""
    (output_dir / "protocol_schematic_caption_20260630.md").write_text(note)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = {name: load_pair(spec["path"], spec["pair_id"]) for name, spec in PAIR_SPECS.items()}
    fig = build_figure(pairs)

    stem = OUTPUT_DIR / "protocol_schematic_figure_20260630"
    fig.savefig(stem.with_suffix(".png"), dpi=220, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    write_caption_note(OUTPUT_DIR)


if __name__ == "__main__":
    main()
