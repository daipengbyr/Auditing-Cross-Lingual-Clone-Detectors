#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute unified Phase 5 preserving/breaking paired metrics.")
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--original-predictions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--tag", default="default")

    parser.add_argument("--preserving-pilot-jsonl", type=Path)
    parser.add_argument("--preserving-model-input-jsonl", type=Path)
    parser.add_argument("--preserving-predictions", type=Path)

    parser.add_argument("--breaking-pilot-jsonl", type=Path)
    parser.add_argument("--breaking-model-input-jsonl", type=Path)
    parser.add_argument("--breaking-predictions", type=Path)
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


def load_rows(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path) if path.suffix == ".jsonl" else load_json(path)


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
    return None if value is None else float(value)


def pct(num: int, den: int) -> float | None:
    return (num / den) if den else None


def mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def align_variant_predictions(model_input_rows: list[dict[str, Any]], prediction_rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], str]:
    prediction_map = {row["pair_id"]: row for row in prediction_rows}
    direct_matches = sum(1 for row in model_input_rows if row["split_pair_id"] in prediction_map)
    if direct_matches > 0:
        return (
            {
                row["split_pair_id"]: prediction_map[row["split_pair_id"]]
                for row in model_input_rows
                if row["split_pair_id"] in prediction_map
            },
            "split_pair_id",
        )
    if len(model_input_rows) == len(prediction_rows):
        return (
            {model_input_rows[idx]["split_pair_id"]: prediction_rows[idx] for idx in range(len(model_input_rows))},
            "row_order",
        )
    return {}, "unresolved"


def build_variant_rows(
    *,
    model_name: str,
    tag: str,
    variant_name: str,
    original_rows: list[dict[str, Any]],
    pilot_rows: list[dict[str, Any]],
    model_input_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    original_map = {row["pair_id"]: row for row in original_rows}
    pilot_map = {row["source_pair_id"]: row for row in pilot_rows}
    pred_by_split_pair_id, alignment = align_variant_predictions(model_input_rows, prediction_rows)

    pair_rows: list[dict[str, Any]] = []
    for variant_input in model_input_rows:
        source_pair_id = variant_input["source_pair_id"]
        orig = original_map.get(source_pair_id)
        pred = pred_by_split_pair_id.get(variant_input["split_pair_id"])
        pilot = pilot_map.get(source_pair_id)
        if orig is None or pred is None:
            continue
        orig_clone = pred_is_clone(orig)
        variant_clone = pred_is_clone(pred)
        orig_prob = prob_yes(orig)
        variant_prob = prob_yes(pred)
        pair_rows.append(
            {
                "model": model_name,
                "tag": tag,
                "variant_name": variant_name,
                "source_pair_id": source_pair_id,
                "variant_pair_id": variant_input["split_pair_id"],
                "lang_b": variant_input["ll2"],
                "problem_id": variant_input["problem_id_1"],
                "transformation_type": variant_input.get("transformation_type"),
                "validation_status": variant_input.get("validation_status"),
                "original_prediction_text": orig.get("prediction_text"),
                "original_prediction_is_clone": orig_clone,
                "original_prob_yes": orig_prob,
                "variant_prediction_text": pred.get("prediction_text"),
                "variant_prediction_is_clone": variant_clone,
                "variant_prob_yes": variant_prob,
                "decision_consistent": orig_clone == variant_clone,
                "decision_changed": orig_clone != variant_clone,
                "clone_preserved": orig_clone and variant_clone,
                "clone_rejected": orig_clone and (not variant_clone),
                "prob_yes_drop": (orig_prob - variant_prob) if (orig_prob is not None and variant_prob is not None) else None,
                "rename_map": json.dumps((pilot or {}).get("rename_map", {}), ensure_ascii=False),
                "semantic_variant_kind": variant_input.get("semantic_variant_kind"),
            }
        )

    total = len(pair_rows)
    orig_yes_rows = [r for r in pair_rows if r["original_prediction_is_clone"]]
    variant_yes_rows = [r for r in pair_rows if r["variant_prediction_is_clone"]]
    changed_rows = [r for r in pair_rows if r["decision_changed"]]
    rejected_rows = [r for r in pair_rows if r["clone_rejected"]]
    prob_drop_rows = [r["prob_yes_drop"] for r in pair_rows if r["prob_yes_drop"] is not None]

    if variant_name == "preserving":
        summary = {
            "model": model_name,
            "tag": tag,
            "variant_name": variant_name,
            "pair_id_alignment": alignment,
            "n_pairs": total,
            "n_original_yes": len(orig_yes_rows),
            "n_variant_yes": len(variant_yes_rows),
            "preservation_consistency_rate": pct(len([r for r in orig_yes_rows if r["variant_prediction_is_clone"]]), len(orig_yes_rows)),
            "overall_decision_consistency_rate": pct(total - len(changed_rows), total),
            "clone_acceptance_drop": (pct(len(orig_yes_rows), total) - pct(len(variant_yes_rows), total)) if total else None,
            "mean_prob_yes_drop": mean(prob_drop_rows),
            "n_clone_lost": len(rejected_rows),
        }
    else:
        summary = {
            "model": model_name,
            "tag": tag,
            "variant_name": variant_name,
            "pair_id_alignment": alignment,
            "n_pairs": total,
            "n_original_yes": len(orig_yes_rows),
            "n_variant_yes": len(variant_yes_rows),
            "breaking_rejection_rate": pct(len(rejected_rows), len(orig_yes_rows)),
            "overall_decision_change_rate": pct(len(changed_rows), total),
            "clone_retention_after_breaking": pct(len([r for r in orig_yes_rows if r["variant_prediction_is_clone"]]), len(orig_yes_rows)),
            "mean_prob_yes_drop": mean(prob_drop_rows),
            "n_clone_rejected": len(rejected_rows),
        }

    per_lang_rows = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[row["lang_b"]].append(row)
    for lang, rows in sorted(grouped.items()):
        orig_yes = [r for r in rows if r["original_prediction_is_clone"]]
        variant_yes = [r for r in rows if r["variant_prediction_is_clone"]]
        changed = [r for r in rows if r["decision_changed"]]
        rejected = [r for r in rows if r["clone_rejected"]]
        prob_drops = [r["prob_yes_drop"] for r in rows if r["prob_yes_drop"] is not None]
        row_out = {
            "model": model_name,
            "tag": tag,
            "variant_name": variant_name,
            "lang_b": lang,
            "n_pairs": len(rows),
            "n_original_yes": len(orig_yes),
            "n_variant_yes": len(variant_yes),
            "mean_prob_yes_drop": mean(prob_drops),
        }
        if variant_name == "preserving":
            row_out["preservation_consistency_rate"] = pct(len([r for r in orig_yes if r["variant_prediction_is_clone"]]), len(orig_yes))
            row_out["overall_decision_consistency_rate"] = pct(len(rows) - len(changed), len(rows))
        else:
            row_out["breaking_rejection_rate"] = pct(len(rejected), len(orig_yes))
            row_out["overall_decision_change_rate"] = pct(len(changed), len(rows))
        per_lang_rows.append(row_out)

    return pair_rows, {"summary": summary, "per_language": per_lang_rows}


def build_contrast_rows(
    model_name: str,
    tag: str,
    preserving_rows: list[dict[str, Any]],
    breaking_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    preserve_map = {row["source_pair_id"]: row for row in preserving_rows}
    break_map = {row["source_pair_id"]: row for row in breaking_rows}
    shared_ids = sorted(set(preserve_map) & set(break_map))

    contrast_rows: list[dict[str, Any]] = []
    for source_pair_id in shared_ids:
        prow = preserve_map[source_pair_id]
        brow = break_map[source_pair_id]
        contrast_rows.append(
            {
                "model": model_name,
                "tag": tag,
                "source_pair_id": source_pair_id,
                "lang_b": prow["lang_b"],
                "problem_id": prow["problem_id"],
                "original_prediction_is_clone": prow["original_prediction_is_clone"],
                "preserving_prediction_is_clone": prow["variant_prediction_is_clone"],
                "breaking_prediction_is_clone": brow["variant_prediction_is_clone"],
                "preserve_yes_break_no": prow["variant_prediction_is_clone"] and (not brow["variant_prediction_is_clone"]),
                "directionally_correct": prow["original_prediction_is_clone"] and prow["variant_prediction_is_clone"] and (not brow["variant_prediction_is_clone"]),
                "directionally_wrong": prow["original_prediction_is_clone"] and (not prow["variant_prediction_is_clone"]) and brow["variant_prediction_is_clone"],
                "preserving_transformation_type": prow["transformation_type"],
                "breaking_transformation_type": brow["transformation_type"],
            }
        )

    original_yes_rows = [r for r in contrast_rows if r["original_prediction_is_clone"]]
    summary = {
        "model": model_name,
        "tag": tag,
        "n_shared_pairs": len(contrast_rows),
        "n_original_yes_shared": len(original_yes_rows),
        "preserve_yes_break_no_rate": pct(len([r for r in original_yes_rows if r["preserve_yes_break_no"]]), len(original_yes_rows)),
        "directional_success_rate": pct(len([r for r in original_yes_rows if r["directionally_correct"]]), len(original_yes_rows)),
        "directional_failure_rate": pct(len([r for r in original_yes_rows if r["directionally_wrong"]]), len(original_yes_rows)),
        "preserving_yes_rate_shared": pct(len([r for r in original_yes_rows if r["preserving_prediction_is_clone"]]), len(original_yes_rows)),
        "breaking_yes_rate_shared": pct(len([r for r in original_yes_rows if r["breaking_prediction_is_clone"]]), len(original_yes_rows)),
        "semantic_gap": (
            pct(len([r for r in original_yes_rows if r["preserving_prediction_is_clone"]]), len(original_yes_rows))
            - pct(len([r for r in original_yes_rows if r["breaking_prediction_is_clone"]]), len(original_yes_rows))
            if original_yes_rows else None
        ),
    }
    return contrast_rows, summary


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve() / f"phase5_unified_{args.model_name}_{args.tag}"
    output_dir.mkdir(parents=True, exist_ok=True)

    original_rows = load_rows(args.original_predictions.resolve())
    result_payload: dict[str, Any] = {
        "model": args.model_name,
        "tag": args.tag,
    }

    preserving_pair_rows: list[dict[str, Any]] = []
    breaking_pair_rows: list[dict[str, Any]] = []

    if args.preserving_pilot_jsonl and args.preserving_model_input_jsonl and args.preserving_predictions:
        preserving_pair_rows, preserving_payload = build_variant_rows(
            model_name=args.model_name,
            tag=args.tag,
            variant_name="preserving",
            original_rows=original_rows,
            pilot_rows=load_jsonl(args.preserving_pilot_jsonl.resolve()),
            model_input_rows=load_jsonl(args.preserving_model_input_jsonl.resolve()),
            prediction_rows=load_rows(args.preserving_predictions.resolve()),
        )
        write_csv(output_dir / "preserving_pair_rows.csv", preserving_pair_rows)
        write_csv(output_dir / "preserving_per_language.csv", preserving_payload["per_language"])
        result_payload["preserving"] = preserving_payload["summary"]

    if args.breaking_pilot_jsonl and args.breaking_model_input_jsonl and args.breaking_predictions:
        breaking_pair_rows, breaking_payload = build_variant_rows(
            model_name=args.model_name,
            tag=args.tag,
            variant_name="breaking",
            original_rows=original_rows,
            pilot_rows=load_jsonl(args.breaking_pilot_jsonl.resolve()),
            model_input_rows=load_jsonl(args.breaking_model_input_jsonl.resolve()),
            prediction_rows=load_rows(args.breaking_predictions.resolve()),
        )
        write_csv(output_dir / "breaking_pair_rows.csv", breaking_pair_rows)
        write_csv(output_dir / "breaking_per_language.csv", breaking_payload["per_language"])
        result_payload["breaking"] = breaking_payload["summary"]

    if preserving_pair_rows and breaking_pair_rows:
        contrast_rows, contrast_summary = build_contrast_rows(
            args.model_name,
            args.tag,
            preserving_pair_rows,
            breaking_pair_rows,
        )
        write_csv(output_dir / "preserving_vs_breaking_contrast_rows.csv", contrast_rows)
        result_payload["contrast"] = contrast_summary

    write_json(output_dir / "phase5_unified_summary.json", result_payload)
    print(json.dumps({"output_dir": str(output_dir), "summary": result_payload}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
