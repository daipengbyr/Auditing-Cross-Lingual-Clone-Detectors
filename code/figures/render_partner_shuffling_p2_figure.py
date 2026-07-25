#!/usr/bin/env python3
"""Render Figure 6: decision transitions under P2 partner shuffling."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


OUT_DIR = Path("outputs/paper_figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)
BASE = OUT_DIR / "figure6_partner_shuffling_p2"


def save_pub(fig, stem: Path, dpi: int = 600) -> None:
    fig.savefig(f"{stem}.svg", bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(f"{stem}.png", dpi=dpi, bbox_inches="tight")
    fig.savefig(f"{stem}.tiff", dpi=dpi, bbox_inches="tight")


def main() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.4,
            "legend.fontsize": 7.4,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
        }
    )

    rows = [
        ("GraphCodeBERT", "B1 random", 0.7033, 0.9242, 0.0800),
        ("GraphCodeBERT", "B2 length-matched", 0.7033, 0.8389, 0.1433),
        ("GraphCodeBERT", "B3 structure-matched", 0.7033, 0.8436, 0.1367),
        ("UniXcoder", "B1 random", 0.6100, 0.9180, 0.0967),
        ("UniXcoder", "B2 length-matched", 0.6100, 0.9016, 0.0867),
        ("UniXcoder", "B3 structure-matched", 0.6100, 0.9016, 0.0900),
        ("Embedding + SVM", "B1 random", 0.6733, 0.4653, 0.4600),
        ("Embedding + SVM", "B2 length-matched", 0.6733, 0.4356, 0.4933),
        ("Embedding + SVM", "B3 structure-matched", 0.6733, 0.4505, 0.4833),
        ("DeepSeek-v4-flash", "B1 random", 0.5933, 1.0000, 0.0000),
        ("DeepSeek-v4-flash", "B2 length-matched", 0.5933, 1.0000, 0.0000),
        ("DeepSeek-v4-flash", "B3 structure-matched", 0.5933, 1.0000, 0.0000),
    ]
    df = pd.DataFrame(rows, columns=["model", "variant", "oca", "cdfr", "shuffled_clone_rate"])
    df["original_not_accepted"] = 1.0 - df["oca"]
    df["accepted_then_rejected"] = df["oca"] * df["cdfr"]
    df["accepted_still_clone"] = df["oca"] * (1.0 - df["cdfr"])
    df["other_shuffled_false_accept"] = (
        df["shuffled_clone_rate"] - df["accepted_still_clone"]
    ).clip(lower=0)
    df.to_csv(f"{BASE}_source_data.csv", index=False)

    colors = {
        "original_not_accepted": "#D9D9D9",
        "accepted_then_rejected": "#79A7A5",
        "accepted_still_clone": "#C96F5B",
    }
    labels = {
        "original_not_accepted": "Not accepted originally",
        "accepted_then_rejected": "Accepted \u2192 rejected",
        "accepted_still_clone": "Accepted \u2192 still accepted",
    }

    models = ["GraphCodeBERT", "UniXcoder", "Embedding + SVM", "DeepSeek-v4-flash"]
    variants = ["B1 random", "B2 length-matched", "B3 structure-matched"]

    bar_h = 0.54
    gap = 0.52
    y_positions = []
    y_labels = []
    current = 0.0
    for model in models:
        for variant in variants:
            y_positions.append(current)
            y_labels.append(variant)
            current += 1.0
        current += gap

    fig, ax = plt.subplots(figsize=(7.05, 4.55))
    for y, (_, row) in zip(y_positions, df.iterrows()):
        left = 0.0
        for key in ["original_not_accepted", "accepted_then_rejected", "accepted_still_clone"]:
            width = float(row[key])
            ax.barh(
                y,
                width,
                left=left,
                height=bar_h,
                color=colors[key],
                edgecolor="white",
                linewidth=0.8,
                label=labels[key],
                zorder=3,
            )
            left += width

    # Add light group separators.
    for sep in [2.5, 6.02, 9.54]:
        ax.axhline(sep, color="#E4E4E4", linewidth=0.8, zorder=0)

    # Put model names on the right to keep the left axis dedicated to variants.
    group_centers = {
        "GraphCodeBERT": sum(y_positions[0:3]) / 3,
        "UniXcoder": sum(y_positions[3:6]) / 3,
        "Embedding + SVM": sum(y_positions[6:9]) / 3,
        "DeepSeek-v4-flash": sum(y_positions[9:12]) / 3,
    }
    for model, y in group_centers.items():
        ax.text(
            1.015,
            y,
            model,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="center",
            fontsize=8.0,
            fontweight="bold",
            color="#2F3A3D",
            clip_on=False,
        )

    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Proportion of original positive P2 code pairs")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels)
    ax.invert_yaxis()
    ax.grid(axis="x", color="#E9E9E9", linewidth=0.8, zorder=0)
    ax.set_title(
        "Partner-shuffling decision transitions under P2",
        loc="left",
        fontweight="bold",
        pad=10,
    )

    # Deduplicate legend entries.
    handles, leg_labels = ax.get_legend_handles_labels()
    dedup = dict(zip(leg_labels, handles))
    ax.legend(
        dedup.values(),
        dedup.keys(),
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.115),
        columnspacing=1.35,
        handlelength=1.4,
    )

    save_pub(fig, BASE)


if __name__ == "__main__":
    main()
