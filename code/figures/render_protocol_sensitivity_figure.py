from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "paper_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_data() -> pd.DataFrame:
    rows = [
        ("GraphCodeBERT", "P0", 0.9848),
        ("GraphCodeBERT", "P1", 0.6341),
        ("GraphCodeBERT", "P2", 0.6588),
        ("UniXcoder", "P0", 0.9916),
        ("UniXcoder", "P1", 0.7533),
        ("UniXcoder", "P2", 0.6970),
        ("Embedding + SVM", "P0", 0.9449),
        ("Embedding + SVM", "P1", 0.6335),
        ("Embedding + SVM", "P2", 0.6372),
        ("DeepSeek-7B", "P0", 0.2571),
        ("DeepSeek-7B", "P1", 0.3118),
        ("DeepSeek-7B", "P2", 0.3230),
        ("DeepSeek-v4-flash", "P0", 0.9269),
        ("DeepSeek-v4-flash", "P1", 0.9111),
        ("DeepSeek-v4-flash", "P2", 0.8868),
    ]
    df = pd.DataFrame(rows, columns=["Model", "Protocol", "F1"])
    p0 = df[df["Protocol"] == "P0"].set_index("Model")["F1"]
    df["Delta_from_P0"] = [
        np.nan if protocol == "P0" else p0[model] - f1
        for model, protocol, f1 in df[["Model", "Protocol", "F1"]].itertuples(index=False)
    ]
    return df


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


def render() -> None:
    setup_style()
    df = build_data()
    df.to_csv(OUT_DIR / "figure_protocol_sensitivity_source_data.csv", index=False)

    models = [
        "GraphCodeBERT",
        "UniXcoder",
        "Embedding + SVM",
        "DeepSeek-7B",
        "DeepSeek-v4-flash",
    ]
    protocols = ["P0", "P1", "P2"]
    x = np.arange(len(protocols))

    colors = {
        "GraphCodeBERT": "#386cb0",
        "UniXcoder": "#7b3294",
        "Embedding + SVM": "#4d9221",
        "DeepSeek-7B": "#7f7f7f",
        "DeepSeek-v4-flash": "#006d77",
    }
    markers = {
        "GraphCodeBERT": "o",
        "UniXcoder": "s",
        "Embedding + SVM": "^",
        "DeepSeek-7B": "v",
        "DeepSeek-v4-flash": "D",
    }

    fig = plt.figure(figsize=(7.1, 3.05))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.18, 1.0], wspace=0.55)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    label_offsets = {
        "DeepSeek-v4-flash": 0.030,
        "UniXcoder": 0.012,
        "GraphCodeBERT": 0.020,
        "Embedding + SVM": -0.018,
        "DeepSeek-7B": 0.000,
    }
    for model in models:
        y = [
            df[(df["Model"] == model) & (df["Protocol"] == protocol)]["F1"].iloc[0]
            for protocol in protocols
        ]
        ax1.plot(
            x,
            y,
            color=colors[model],
            marker=markers[model],
            linewidth=1.35,
            markersize=4.0,
        )
        ax1.text(
            x[-1] + 0.07,
            y[-1] + label_offsets.get(model, 0.0),
            model,
            va="center",
            ha="left",
            fontsize=6.2,
            color=colors[model],
        )
    ax1.set_title("(a) F1 under progressively stricter protocols", loc="left", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(protocols)
    ax1.set_ylabel("F1")
    ax1.set_xlim(-0.13, 2.86)
    ax1.set_ylim(0.18, 1.04)
    ax1.set_yticks(np.arange(0.2, 1.01, 0.2))
    ax1.grid(axis="y", color="#e6e6e6", linewidth=0.6)

    delta = df[df["Protocol"].isin(["P1", "P2"])].copy()
    y_positions = np.arange(len(models))
    bar_h = 0.32
    offsets = {"P1": -bar_h / 2, "P2": bar_h / 2}
    hatch = {"P1": "", "P2": "////"}
    labels = {"P1": r"$\Delta_{P0\to P1}$", "P2": r"$\Delta_{P0\to P2}$"}

    for protocol in ["P1", "P2"]:
        vals = [
            delta[(delta["Model"] == model) & (delta["Protocol"] == protocol)][
                "Delta_from_P0"
            ].iloc[0]
            for model in models
        ]
        ax2.barh(
            y_positions + offsets[protocol],
            vals,
            height=bar_h,
            color="#9fb7bd" if protocol == "P1" else "#d6e2e4",
            edgecolor="#3f5960",
            linewidth=0.55,
            hatch=hatch[protocol],
            label=labels[protocol],
        )
        for ypos, val in zip(y_positions + offsets[protocol], vals):
            ha = "left" if val >= 0 else "right"
            dx = 0.008 if val >= 0 else -0.015
            ax2.text(
                val + dx,
                ypos,
                f"{val:+.3f}",
                va="center",
                ha=ha,
                fontsize=6.2,
                color="#37474f",
            )

    ax2.axvline(0, color="#6f6f6f", linewidth=0.75)
    ax2.set_title("(b) F1 drop relative to P0", loc="left", fontweight="bold")
    ax2.set_yticks(y_positions)
    ax2.set_yticklabels(models)
    ax2.invert_yaxis()
    ax2.set_xlabel(r"$\Delta=\mathrm{F1}(P0)-\mathrm{F1}(Pk)$")
    ax2.set_xlim(-0.14, 0.40)
    ax2.set_xticks(np.arange(-0.1, 0.41, 0.1))
    ax2.grid(axis="x", color="#e6e6e6", linewidth=0.6)
    ax2.legend(loc="lower right", fontsize=6.3, handlelength=1.7)
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.18, top=0.88, wspace=0.55)
    base = OUT_DIR / "figure_protocol_sensitivity_p0_p2"
    fig.savefig(f"{base}.svg", bbox_inches="tight")
    fig.savefig(f"{base}.pdf", bbox_inches="tight")
    fig.savefig(f"{base}.png", dpi=600, bbox_inches="tight")
    fig.savefig(f"{base}.tiff", dpi=600, bbox_inches="tight")


if __name__ == "__main__":
    render()
