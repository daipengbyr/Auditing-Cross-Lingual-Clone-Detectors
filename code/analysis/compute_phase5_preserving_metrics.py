#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT_JSONL = ROOT / "outputs" / "third_round_phase5_preserving_pilot_20260627" / "semantic_preserving_pilot.jsonl"
DEFAULT_MODEL_INPUT_JSONL = ROOT / "outputs" / "third_round_phase5_preserving_pilot_20260627" / "semantic_preserving_model_input.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "third_round_phase5_preserving_pilot_20260627"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute Phase 5A semantic-preserving metrics.")
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--original-predictions", type=Path, required=True)
    parser.add_argument("--preserving-predictions", type=Path, required=True)
    parser.add_argument("--pilot-jsonl", type=Path, default=DEFAULT_PILOT_JSONL)
    parser.add_argument("--model-input-jsonl", type=Path, default=DEFAULT_MODEL_INPUT_JSONL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--tag", default="default")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pred_is_clone(row: dict[str, Any]) -> bool:
    if "prediction_is_clone" in row:
        return bool(row["prediction_is_clone"])
    return str(row.get("prediction_text", "")).strip().lower() == "yes"


def prob_yes(row: dict[str, Any]) -> float | None:
    value = row.get("prob_yes")
    if value is None:
        value = row.get("confidence")
    if value is None:
        return None
    return float(value)


def mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def pct(num: int, den: int) -> float | None:
    return (num / den) if den else None


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve() / f"preserving_metrics_{args.model_name}_{args.tag}"
    output_dir.mkdir(parents=True, exist_ok=True)

    original_path = args.original_predictions.resolve()
    original_rows = load_jsonl(original_path) if original_path.suffix == ".jsonl" else load_json(original_path)
    preserving_rows = (
        load_jsonl(args.preserving_predictions.resolve())
        if args.preserving_predictions.suffix == ".jsonl"
        else load_json(args.preserving_predictions.resolve())
    )
    pilot_rows = load_jsonl(args.pilot_jsonl.resolve())
    model_input_rows = load_jsonl(args.model_input_jsonl.resolve())

    original_map = {row["pair_id"]: row for row in original_rows}
    pilot_map = {row["source_pair_id"]: row for row in pilot_rows}
    model_input_map = {row["split_pair_id"]: row for row in model_input_rows}
    preserving_map = {row["pair_id"]: row for row in preserving_rows}

    preserving_by_split_pair_id: dict[str, dict[str, Any]] = {}
    direct_matches = sum(1 for pair_id in model_input_map if pair_id in preserving_map)
    if direct_matches > 0:
        preserving_by_split_pair_id = {
            split_pair_id: preserving_map[split_pair_id]
            for split_pair_id in model_input_map
            if split_pair_id in preserving_map
        }
        pair_id_alignment = "split_pair_id"
    elif len(preserving_rows) == len(model_input_rows):
        preserving_by_split_pair_id = {
            model_input_rows[idx]["split_pair_id"]: preserving_rows[idx]
            for idx in range(len(model_input_rows))
        }
        pair_id_alignment = "row_order"
    else:
        pair_id_alignment = "unresolved"

    pair_rows: list[dict[str, Any]] = []
    for variant_pair_id, variant_input in model_input_map.items():
        source_pair_id = variant_input["source_pair_id"]
        orig = original_map.get(source_pair_id)
        pred = preserving_by_split_pair_id.get(variant_pair_id)
        pilot = pilot_map.get(source_pair_id)
        if orig is None or pred is None or pilot is None:
            continue
        orig_clone = pred_is_clone(orig)
        preserve_clone = pred_is_clone(pred)
        orig_prob = prob_yes(orig)
        preserve_prob = prob_yes(pred)
        pair_rows.append(
            {
                "model": args.model_name,
                "tag": args.tag,
                "source_pair_id": source_pair_id,
                "preserving_pair_id": variant_pair_id,
                "lang_b": variant_input["ll2"],
                "problem_id": variant_input["problem_id_1"],
                "validation_status": variant_input.get("validation_status"),
                "transformation_type": variant_input.get("transformation_type"),
                "original_prediction_text": orig.get("prediction_text"),
                "original_prediction_is_clone": orig_clone,
                "original_prob_yes": orig_prob,
                "preserving_prediction_text": pred.get("prediction_text"),
                "preserving_prediction_is_clone": preserve_clone,
                "preserving_prob_yes": preserve_prob,
                "decision_consistent": orig_clone == preserve_clone,
                "clone_preserved": orig_clone and preserve_clone,
                "clone_lost": orig_clone and (not preserve_clone),
                "prob_yes_drop": (orig_prob - preserve_prob) if (orig_prob is not None and preserve_prob is not None) else None,
                "rename_map": json.dumps(pilot.get("rename_map", {}), ensure_ascii=False),
            }
        )

    total = len(pair_rows)
    orig_yes_rows = [r for r in pair_rows if r["original_prediction_is_clone"]]
    preserve_yes_rows = [r for r in pair_rows if r["preserving_prediction_is_clone"]]
    clone_loss_rows = [r for r in pair_rows if r["clone_lost"]]
    consistent_rows = [r for r in pair_rows if r["decision_consistent"]]
    prob_drop_rows = [r["prob_yes_drop"] for r in pair_rows if r["prob_yes_drop"] is not None]

    summary = {
        "model": args.model_name,
        "tag": args.tag,
        "pair_id_alignment": pair_id_alignment,
        "n_pairs": total,
        "n_original_yes": len(orig_yes_rows),
        "n_preserving_yes": len(preserve_yes_rows),
        "preservation_consistency_rate": pct(len([r for r in orig_yes_rows if r["preserving_prediction_is_clone"]]), len(orig_yes_rows)),
        "overall_decision_consistency_rate": pct(len(consistent_rows), total),
        "clone_acceptance_drop": (
            pct(len(orig_yes_rows), total) - pct(len(preserve_yes_rows), total)
            if total else None
        ),
        "mean_prob_yes_drop": mean(prob_drop_rows),
        "n_clone_lost": len(clone_loss_rows),
    }

    per_lang_rows = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[row["lang_b"]].append(row)
    for lang, rows in sorted(grouped.items()):
        orig_yes = [r for r in rows if r["original_prediction_is_clone"]]
        preserve_yes = [r for r in rows if r["preserving_prediction_is_clone"]]
        prob_drops = [r["prob_yes_drop"] for r in rows if r["prob_yes_drop"] is not None]
        per_lang_rows.append(
            {
                "model": args.model_name,
                "tag": args.tag,
                "lang_b": lang,
                "n_pairs": len(rows),
                "n_original_yes": len(orig_yes),
                "n_preserving_yes": len(preserve_yes),
                "preservation_consistency_rate": pct(len([r for r in orig_yes if r["preserving_prediction_is_clone"]]), len(orig_yes)),
                "overall_decision_consistency_rate": pct(len([r for r in rows if r["decision_consistent"]]), len(rows)),
                "clone_acceptance_drop": (
                    pct(len(orig_yes), len(rows)) - pct(len(preserve_yes), len(rows))
                    if rows else None
                ),
                "mean_prob_yes_drop": mean(prob_drops),
            }
        )

    write_csv(output_dir / "semantic_preserving_pair_rows.csv", pair_rows)
    write_csv(output_dir / "semantic_preserving_per_language.csv", per_lang_rows)
    write_json(output_dir / "semantic_preserving_summary.json", summary)
    print(json.dumps({"output_dir": str(output_dir), "summary": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
