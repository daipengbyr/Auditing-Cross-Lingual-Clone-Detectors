#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MIRROR_ROOT = ROOT / "outputs" / "third_round_remote_mirror_20260626"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "third_round_statistics_20260626"

PROTOCOLS = {
    "p2": {
        "split_test": "splits/p2/test.jsonl",
        "run_suffix": "p2",
    },
    "p0-eb": {
        "split_test": "splits/clean_protocol_splits_p0eb_20260625/test.jsonl",
        "run_suffix": "p0eb",
    },
}

MODELS = [
    "graphcodebert",
    "unixcoder",
    "embedding_svm",
    "deepseek_v4_flash",
]

VARIANTS = {
    "b1": {
        "name": "b1_random",
        "prediction_file": "b1_random_predictions.json",
        "shuffled_input_file": "shortcut_sets/partner_shuffled_b1_random.jsonl",
    },
    "b2": {
        "name": "b2_length_matched",
        "prediction_file": "b2_length_matched_predictions.json",
        "shuffled_input_file": "shortcut_sets/partner_shuffled_b2_length_matched.jsonl",
    },
    "b3": {
        "name": "b3_structure_matched",
        "prediction_file": "b3_structure_matched_predictions.json",
        "shuffled_input_file": "shortcut_sets/partner_shuffled_b3_structure_matched.jsonl",
    },
}

RUNS_SUBDIR = "runs/second_round_extensions_20260625"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export original and paired counterfactual sample-level predictions."
    )
    parser.add_argument(
        "--mirror-root",
        type=Path,
        default=DEFAULT_MIRROR_ROOT,
        help="Local mirror root containing splits/ and runs/ subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for exported JSONL/CSV artifacts.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def pred_is_clone(row: dict[str, Any]) -> bool:
    return str(row.get("prediction_text", "")).strip().lower() == "yes"


def prob_yes_and_mode(row: dict[str, Any]) -> tuple[float, str]:
    if row.get("prob_yes") is not None:
        return float(row["prob_yes"]), "native_prob_yes"
    if row.get("confidence") is not None:
        return float(row["confidence"]), "confidence_derived"
    return (1.0 if pred_is_clone(row) else 0.0), "binary_proxy"


def flatten_match_distance(match_distance: Any) -> dict[str, Any]:
    if not isinstance(match_distance, dict):
        return {}
    flattened = {}
    for key, value in match_distance.items():
        flattened[f"match_distance_{key}"] = value
    return flattened


def transition_name(original_clone: bool, shuffled_clone: bool) -> str:
    if original_clone and not shuffled_clone:
        return "clone_to_nonclone"
    if original_clone and shuffled_clone:
        return "clone_to_clone"
    if (not original_clone) and shuffled_clone:
        return "nonclone_to_clone"
    return "nonclone_to_nonclone"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_original_rows(
    protocol: str,
    model: str,
    split_rows: dict[str, dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    exported: list[dict[str, Any]] = []
    for pred_row in prediction_rows:
        pair_id = pred_row["pair_id"]
        split_row = split_rows[pair_id]
        prob_yes, prob_mode = prob_yes_and_mode(pred_row)
        pred_clone = pred_is_clone(pred_row)
        gold_is_clone = split_row["type"] == "clone"
        exported.append(
            {
                "protocol": protocol,
                "model": model,
                "sample_id": pair_id,
                "pair_id": pair_id,
                "label_text": split_row["type"],
                "label_is_clone": gold_is_clone,
                "prediction_text": pred_row.get("prediction_text"),
                "prediction_is_clone": pred_clone,
                "correct": pred_clone == gold_is_clone,
                "prob_yes": prob_yes,
                "prob_mode": prob_mode,
                "lang_a": split_row["ll1"],
                "lang_b": split_row["ll2"],
                "problem_id_a": split_row["problem_id_1"],
                "problem_id_b": split_row["problem_id_2"],
                "normalized_code_hash_a": split_row.get("normalized_code_hash_a"),
                "normalized_code_hash_b": split_row.get("normalized_code_hash_b"),
                "exact_pair_hash": split_row.get("exact_pair_hash"),
            }
        )
    return exported


def export_paired_rows(
    protocol: str,
    model: str,
    split_rows: dict[str, dict[str, Any]],
    original_predictions: dict[str, dict[str, Any]],
    shuffled_inputs: dict[str, dict[str, Any]],
    shuffled_input_rows: list[dict[str, Any]],
    shuffled_prediction_rows: list[dict[str, Any]],
    variant: str,
) -> list[dict[str, Any]]:
    exported: list[dict[str, Any]] = []
    if all(row["pair_id"] in shuffled_inputs for row in shuffled_prediction_rows):
        paired_iter = [
            (row["pair_id"], shuffled_inputs[row["pair_id"]], row)
            for row in shuffled_prediction_rows
        ]
    else:
        if len(shuffled_input_rows) != len(shuffled_prediction_rows):
            raise ValueError(
                f"Cannot align shuffled rows for {protocol}/{model}/{variant}: "
                f"{len(shuffled_input_rows)} inputs vs {len(shuffled_prediction_rows)} predictions."
            )
        paired_iter = []
        for shuffled_input, shuffled_row in zip(shuffled_input_rows, shuffled_prediction_rows):
            if (
                shuffled_input.get("problem_id_1") != shuffled_row.get("problem_id_a")
                or shuffled_input.get("problem_id_2") != shuffled_row.get("problem_id_b")
                or shuffled_input.get("ll1") != shuffled_row.get("lang_a")
                or shuffled_input.get("ll2") != shuffled_row.get("lang_b")
            ):
                raise ValueError(
                    f"Sequential alignment mismatch for {protocol}/{model}/{variant}: "
                    f"input {shuffled_input.get('split_pair_id')} does not match prediction {shuffled_row.get('pair_id')}."
                )
            paired_iter.append((shuffled_input["split_pair_id"], shuffled_input, shuffled_row))

    for source_pair_id, shuffled_input, shuffled_row in paired_iter:
        meta = shuffled_input.get("meta", {})
        source_sample_id = meta["source_sample_id"]
        original_pred = original_predictions[source_sample_id]
        source_split = split_rows[source_sample_id]

        original_prob_yes, original_prob_mode = prob_yes_and_mode(original_pred)
        shuffled_prob_yes, shuffled_prob_mode = prob_yes_and_mode(shuffled_row)
        original_pred_clone = pred_is_clone(original_pred)
        shuffled_pred_clone = pred_is_clone(shuffled_row)

        probability_mode = (
            original_prob_mode
            if original_prob_mode == shuffled_prob_mode
            else f"{original_prob_mode}->{shuffled_prob_mode}"
        )

        match_distance = meta.get("match_distance", {})
        source_problem_ids = meta.get("source_problem_ids") or [
            source_split.get("problem_id_1"),
            source_split.get("problem_id_2"),
        ]

        exported.append(
            {
                "protocol": protocol,
                "model": model,
                "variant": variant,
                "variant_name": VARIANTS[variant]["name"],
                "sample_id": source_sample_id,
                "source_sample_id": source_sample_id,
                "counterfactual_pair_id": shuffled_row["pair_id"],
                "source_pair_id": source_pair_id,
                "original_pair_id": source_sample_id,
                "donor_sample_id": meta.get("donor_sample_id"),
                "donor_problem_id": meta.get("donor_problem_id"),
                "donor_lang_b": meta.get("donor_lang_b"),
                "donor_rank": meta.get("donor_rank"),
                "is_primary_donor": meta.get("is_primary_donor"),
                "shuffle_type": meta.get("shuffle_type"),
                "audit_variant": meta.get("audit_variant"),
                "presumed_label": meta.get("presumed_label"),
                "donor_validation_status": meta.get("donor_validation_status"),
                "generation_seed": meta.get("generation_seed"),
                "source_problem_id_a": source_problem_ids[0] if len(source_problem_ids) > 0 else None,
                "source_problem_id_b": source_problem_ids[1] if len(source_problem_ids) > 1 else None,
                "shuffled_problem_id_a": shuffled_input.get("problem_id_1"),
                "shuffled_problem_id_b": shuffled_input.get("problem_id_2"),
                "lang_a": shuffled_input.get("ll1"),
                "lang_b": shuffled_input.get("ll2"),
                "source_lang_b": meta.get("source_lang_b"),
                "original_label_text": source_split["type"],
                "original_label_is_clone": source_split["type"] == "clone",
                "shuffled_label_text": shuffled_input["type"],
                "shuffled_label_is_clone": shuffled_input["type"] == "clone",
                "original_prediction_text": original_pred.get("prediction_text"),
                "original_prediction_is_clone": original_pred_clone,
                "shuffled_prediction_text": shuffled_row.get("prediction_text"),
                "shuffled_prediction_is_clone": shuffled_pred_clone,
                "original_correct": original_pred_clone,
                "shuffled_correct": not shuffled_pred_clone,
                "decision_any_flip": original_pred_clone != shuffled_pred_clone,
                "decision_flip_clone_to_nonclone": original_pred_clone and (not shuffled_pred_clone),
                "decision_flip_nonclone_to_clone": (not original_pred_clone) and shuffled_pred_clone,
                "transition_type": transition_name(original_pred_clone, shuffled_pred_clone),
                "original_prob_yes": original_prob_yes,
                "shuffled_prob_yes": shuffled_prob_yes,
                "prob_yes_drop": original_prob_yes - shuffled_prob_yes,
                "prob_yes_decreased": original_prob_yes > shuffled_prob_yes,
                "probability_mode": probability_mode,
                "original_prob_mode": original_prob_mode,
                "shuffled_prob_mode": shuffled_prob_mode,
                "counterfactual_uses_binary_proxy": (
                    original_prob_mode == "binary_proxy" or shuffled_prob_mode == "binary_proxy"
                ),
                "original_normalized_code_hash_a": source_split.get("normalized_code_hash_a"),
                "original_normalized_code_hash_b": source_split.get("normalized_code_hash_b"),
                "shuffled_normalized_code_hash_a": shuffled_input.get("normalized_code_hash_a"),
                "shuffled_normalized_code_hash_b": shuffled_input.get("normalized_code_hash_b"),
                "original_exact_pair_hash": source_split.get("exact_pair_hash"),
                "shuffled_exact_pair_hash": shuffled_input.get("exact_pair_hash"),
                "original_code_b_hash": meta.get("original_code_b_hash"),
                "donor_code_b_hash": meta.get("donor_code_b_hash"),
                "original_code_b_token_count": meta.get("original_code_b_token_count"),
                "donor_code_b_token_count": meta.get("donor_code_b_token_count"),
                **flatten_match_distance(match_distance),
            }
        )
    return exported


def main() -> None:
    args = parse_args()
    mirror_root = args.mirror_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    runs_root = mirror_root / RUNS_SUBDIR
    if not runs_root.exists():
        raise FileNotFoundError(f"Runs root not found: {runs_root}")

    original_rows_all: list[dict[str, Any]] = []
    paired_rows_all: list[dict[str, Any]] = []
    export_manifest: dict[str, Any] = {
        "mirror_root": str(mirror_root),
        "runs_root": str(runs_root),
        "protocols": {},
    }

    for protocol, protocol_info in PROTOCOLS.items():
        split_test_path = mirror_root / protocol_info["split_test"]
        split_rows = {
            row["split_pair_id"]: row for row in load_jsonl(split_test_path)
        }
        export_manifest["protocols"][protocol] = {
            "split_test_path": str(split_test_path),
            "n_test_rows": len(split_rows),
            "models": {},
        }

        for model in MODELS:
            run_dir = runs_root / f"{model}_{protocol_info['run_suffix']}"
            original_prediction_path = run_dir / "original_test_predictions.json"
            original_predictions_list = load_json(original_prediction_path)
            original_predictions = {
                row["pair_id"]: row for row in original_predictions_list
            }

            original_rows = export_original_rows(
                protocol=protocol,
                model=model,
                split_rows=split_rows,
                prediction_rows=original_predictions_list,
            )
            original_rows_all.extend(original_rows)

            export_manifest["protocols"][protocol]["models"][model] = {
                "run_dir": str(run_dir),
                "original_prediction_path": str(original_prediction_path),
                "n_original_predictions": len(original_predictions_list),
                "variants": {},
            }

            for variant, variant_info in VARIANTS.items():
                shuffled_input_path = run_dir / variant_info["shuffled_input_file"]
                shuffled_prediction_path = run_dir / variant_info["prediction_file"]

                shuffled_input_rows = load_jsonl(shuffled_input_path)
                shuffled_inputs = {
                    row["split_pair_id"]: row for row in shuffled_input_rows
                }
                shuffled_prediction_rows = load_json(shuffled_prediction_path)

                paired_rows = export_paired_rows(
                    protocol=protocol,
                    model=model,
                    split_rows=split_rows,
                    original_predictions=original_predictions,
                    shuffled_inputs=shuffled_inputs,
                    shuffled_input_rows=shuffled_input_rows,
                    shuffled_prediction_rows=shuffled_prediction_rows,
                    variant=variant,
                )
                paired_rows_all.extend(paired_rows)

                export_manifest["protocols"][protocol]["models"][model]["variants"][variant] = {
                    "shuffled_input_path": str(shuffled_input_path),
                    "shuffled_prediction_path": str(shuffled_prediction_path),
                    "n_shuffled_inputs": len(shuffled_input_rows),
                    "n_shuffled_predictions": len(shuffled_prediction_rows),
                    "n_paired_rows": len(paired_rows),
                }

    original_jsonl_path = output_dir / "third_round_original_full_sample_predictions_20260626.jsonl"
    original_csv_path = output_dir / "third_round_original_full_sample_predictions_20260626.csv"
    paired_jsonl_path = output_dir / "third_round_paired_counterfactual_predictions_20260626.jsonl"
    paired_csv_path = output_dir / "third_round_paired_counterfactual_predictions_20260626.csv"
    manifest_path = output_dir / "third_round_prediction_export_manifest_20260626.json"

    write_jsonl(original_jsonl_path, original_rows_all)
    write_csv(original_csv_path, original_rows_all)
    write_jsonl(paired_jsonl_path, paired_rows_all)
    write_csv(paired_csv_path, paired_rows_all)
    manifest_path.write_text(
        json.dumps(
            {
                **export_manifest,
                "outputs": {
                    "original_jsonl": str(original_jsonl_path),
                    "original_csv": str(original_csv_path),
                    "paired_jsonl": str(paired_jsonl_path),
                    "paired_csv": str(paired_csv_path),
                },
                "n_original_rows_total": len(original_rows_all),
                "n_paired_rows_total": len(paired_rows_all),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps(
        {
            "original_rows": len(original_rows_all),
            "paired_rows": len(paired_rows_all),
            "output_dir": str(output_dir),
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
