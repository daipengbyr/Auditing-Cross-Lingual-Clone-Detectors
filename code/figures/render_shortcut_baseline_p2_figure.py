from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "paper_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "xtick.major.width": 0.7,
            "ytick.major.width": 0.7,
            "legend.frameon": False,
        }
    )


def build_data() -> pd.DataFrame:
    rows = [
        ("A1 hash lookup", 0.0000, 0.3333, 0.5000, 0.0000),
        ("A2 code-A only", 0.0000, 0.3333, 0.5000, 0.0000),
        ("A3 code-B only", 0.0000, 0.3333, 0.5000, 0.0000),
        ("A4-lite surface", 0.6215, 0.5987, 0.6000, 0.5567),
        ("Shallow Control", 0.6889, 0.7042, 0.7050, 0.4483),
    ]
    return pd.DataFrame(
        rows,
        columns=["Shortcut view", "F1", "Macro-F1", "Balanced accuracy", "Predicted positive rate"],
    )


def render() -> None:
    setup_style()
    df = build_data()
    df.to_csv(OUT_DIR / "figure5_shortcut_baseline_p2_source_data.csv", index=False)

    fig, ax = plt.subplots(figsize=(3.55, 2.35))
    y = np.arange(len(df))
    values = df["Balanced accuracy"].to_numpy()
    colors = ["#d8d8d8", "#d8d8d8", "#d8d8d8", "#9fb7bd", "#006d77"]
    edges = ["#777777", "#777777", "#777777", "#46646b", "#00535b"]

    ax.barh(y, values, color=colors, edgecolor=edges, linewidth=0.75, height=0.62)
    ax.axvline(0.5, color="#7a7a7a", linestyle="--", linewidth=0.8)
    ax.text(0.505, -0.62, "chance", ha="left", va="center", fontsize=6.3, color="#666666")

    for ypos, value in zip(y, values):
        ax.text(value + 0.012, ypos, f"{value:.3f}", va="center", ha="left", fontsize=6.5)

    ax.set_yticks(y)
    ax.set_yticklabels(df["Shortcut view"])
    ax.invert_yaxis()
    ax.set_xlabel("Balanced accuracy under P2")
    ax.set_xlim(0.0, 0.78)
    ax.set_xticks(np.arange(0, 0.81, 0.2))
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.6)
    ax.set_title("Shortcut baseline performance under P2", loc="left", fontweight="bold", pad=5)

    fig.subplots_adjust(left=0.36, right=0.97, bottom=0.20, top=0.88)
    base = OUT_DIR / "figure5_shortcut_baseline_p2"
    fig.savefig(f"{base}.svg", bbox_inches="tight")
    fig.savefig(f"{base}.pdf", bbox_inches="tight")
    fig.savefig(f"{base}.png", dpi=600, bbox_inches="tight")
    fig.savefig(f"{base}.tiff", dpi=600, bbox_inches="tight")


if __name__ == "__main__":
    render()
