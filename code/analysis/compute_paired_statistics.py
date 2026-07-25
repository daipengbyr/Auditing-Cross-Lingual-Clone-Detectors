#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "outputs" / "third_round_statistics_20260626"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute bootstrap confidence intervals and paired tests."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing exported sample-level prediction files.",
    )
    parser.add_argument(
        "--bootstrap-iters",
        type=int,
        default=2000,
        help="Number of bootstrap resamples.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260626,
        help="Random seed.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def group_by(rows: list[dict[str, Any]], *keys: str) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    return grouped


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def bootstrap_ci(
    rows: list[dict[str, Any]],
    metric_fn: Callable[[list[dict[str, Any]]], float],
    rng: random.Random,
    iters: int,
) -> tuple[float, float, float]:
    point = metric_fn(rows)
    if not rows:
        return point, float("nan"), float("nan")
    boot = []
    n = len(rows)
    for _ in range(iters):
        sample = [rows[rng.randrange(n)] for _ in range(n)]
        boot.append(metric_fn(sample))
    return point, percentile(boot, 0.025), percentile(boot, 0.975)


def bootstrap_paired_diff_ci(
    paired_rows: list[tuple[dict[str, Any], dict[str, Any]]],
    metric_fn: Callable[[list[dict[str, Any]]], float],
    rng: random.Random,
    iters: int,
) -> tuple[float, float, float]:
    left_rows = [pair[0] for pair in paired_rows]
    right_rows = [pair[1] for pair in paired_rows]
    point = metric_fn(left_rows) - metric_fn(right_rows)
    if not paired_rows:
        return point, float("nan"), float("nan")
    boot = []
    n = len(paired_rows)
    for _ in range(iters):
        sample_pairs = [paired_rows[rng.randrange(n)] for _ in range(n)]
        boot.append(
            metric_fn([pair[0] for pair in sample_pairs])
            - metric_fn([pair[1] for pair in sample_pairs])
        )
    return point, percentile(boot, 0.025), percentile(boot, 0.975)


def exact_mcnemar_pvalue(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def metric_accuracy(rows: list[dict[str, Any]]) -> float:
    return safe_div(sum(1 for row in rows if row["correct"]), len(rows))


def metric_precision(rows: list[dict[str, Any]]) -> float:
    tp = sum(1 for row in rows if row["prediction_is_clone"] and row["label_is_clone"])
    fp = sum(1 for row in rows if row["prediction_is_clone"] and (not row["label_is_clone"]))
    return safe_div(tp, tp + fp)


def metric_recall(rows: list[dict[str, Any]]) -> float:
    tp = sum(1 for row in rows if row["prediction_is_clone"] and row["label_is_clone"])
    fn = sum(1 for row in rows if (not row["prediction_is_clone"]) and row["label_is_clone"])
    return safe_div(tp, tp + fn)


def metric_f1(rows: list[dict[str, Any]]) -> float:
    precision = metric_precision(rows)
    recall = metric_recall(rows)
    return safe_div(2 * precision * recall, precision + recall)


def metric_oca(rows: list[dict[str, Any]]) -> float:
    return safe_div(sum(1 for row in rows if row["original_prediction_is_clone"]), len(rows))


def metric_ssr(rows: list[dict[str, Any]]) -> float:
    return safe_div(sum(1 for row in rows if not row["shuffled_prediction_is_clone"]), len(rows))


def metric_cpa(rows: list[dict[str, Any]]) -> float:
    return safe_div(sum(1 for row in rows if row["decision_flip_clone_to_nonclone"]), len(rows))


def metric_cdfr(rows: list[dict[str, Any]]) -> float:
    subset = [row for row in rows if row["original_prediction_is_clone"]]
    return safe_div(sum(1 for row in subset if not row["shuffled_prediction_is_clone"]), len(subset))


def metric_urfr(rows: list[dict[str, Any]]) -> float:
    subset = [row for row in rows if not row["original_prediction_is_clone"]]
    return safe_div(sum(1 for row in subset if row["shuffled_prediction_is_clone"]), len(subset))


def metric_pfr(rows: list[dict[str, Any]]) -> float:
    return safe_div(sum(1 for row in rows if row["prob_yes_decreased"]), len(rows))


def metric_cpd(rows: list[dict[str, Any]]) -> float:
    return safe_div(sum(float(row["prob_yes_drop"]) for row in rows), len(rows))


def metric_clone_rate_drop(rows: list[dict[str, Any]]) -> float:
    return metric_oca(rows) - safe_div(
        sum(1 for row in rows if row["shuffled_prediction_is_clone"]),
        len(rows),
    )


COUNTERFACTUAL_METRICS: dict[str, Callable[[list[dict[str, Any]]], float]] = {
    "OCA": metric_oca,
    "SSR": metric_ssr,
    "CPA": metric_cpa,
    "CDFR": metric_cdfr,
    "URFR": metric_urfr,
    "PFR": metric_pfr,
    "CPD": metric_cpd,
    "clone_rate_drop": metric_clone_rate_drop,
}

ORIGINAL_METRICS: dict[str, Callable[[list[dict[str, Any]]], float]] = {
    "accuracy": metric_accuracy,
    "precision": metric_precision,
    "recall": metric_recall,
    "f1": metric_f1,
}


def summarise_prob_modes(rows: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row["probability_mode"])] += 1
    return "; ".join(f"{mode}:{counts[mode]}" for mode in sorted(counts))


def build_original_arrays(rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    return {
        "pred": [1.0 if row["prediction_is_clone"] else 0.0 for row in rows],
        "label": [1.0 if row["label_is_clone"] else 0.0 for row in rows],
        "correct": [1.0 if row["correct"] else 0.0 for row in rows],
    }


def build_counterfactual_arrays(rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    return {
        "original_clone": [1.0 if row["original_prediction_is_clone"] else 0.0 for row in rows],
        "shuffled_clone": [1.0 if row["shuffled_prediction_is_clone"] else 0.0 for row in rows],
        "flip_clone_to_nonclone": [1.0 if row["decision_flip_clone_to_nonclone"] else 0.0 for row in rows],
        "flip_nonclone_to_clone": [1.0 if row["decision_flip_nonclone_to_clone"] else 0.0 for row in rows],
        "prob_yes_decreased": [1.0 if row["prob_yes_decreased"] else 0.0 for row in rows],
        "prob_yes_drop": [float(row["prob_yes_drop"]) for row in rows],
    }


def original_metrics_from_arrays(arrays: dict[str, list[float]], indices: list[int] | None = None) -> dict[str, float]:
    pred = arrays["pred"]
    label = arrays["label"]
    correct = arrays["correct"]
    if indices is None:
        indices = list(range(len(pred)))
    n = len(indices)
    tp = fp = fn = 0.0
    correct_sum = 0.0
    for idx in indices:
        p = pred[idx]
        y = label[idx]
        correct_sum += correct[idx]
        if p and y:
            tp += 1.0
        elif p and (not y):
            fp += 1.0
        elif (not p) and y:
            fn += 1.0
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    return {
        "accuracy": safe_div(correct_sum, n),
        "precision": precision,
        "recall": recall,
        "f1": safe_div(2 * precision * recall, precision + recall),
    }


def counterfactual_metrics_from_arrays(
    arrays: dict[str, list[float]],
    indices: list[int] | None = None,
) -> dict[str, float]:
    original_clone = arrays["original_clone"]
    shuffled_clone = arrays["shuffled_clone"]
    flip_clone_to_nonclone = arrays["flip_clone_to_nonclone"]
    flip_nonclone_to_clone = arrays["flip_nonclone_to_clone"]
    prob_yes_decreased = arrays["prob_yes_decreased"]
    prob_yes_drop = arrays["prob_yes_drop"]
    if indices is None:
        indices = list(range(len(original_clone)))
    n = len(indices)
    o_sum = shuf_clone_sum = cpa_sum = urfr_sum = pfr_sum = cpd_sum = 0.0
    cdfr_num = cdfr_den = 0.0
    urfr_den = 0.0
    for idx in indices:
        o = original_clone[idx]
        sc = shuffled_clone[idx]
        cpa = flip_clone_to_nonclone[idx]
        urf = flip_nonclone_to_clone[idx]
        pfr = prob_yes_decreased[idx]
        cpd = prob_yes_drop[idx]
        o_sum += o
        shuf_clone_sum += sc
        cpa_sum += cpa
        urfr_sum += urf
        pfr_sum += pfr
        cpd_sum += cpd
        if o:
            cdfr_den += 1.0
            if not sc:
                cdfr_num += 1.0
        else:
            urfr_den += 1.0
    ssr_sum = n - shuf_clone_sum
    return {
        "OCA": safe_div(o_sum, n),
        "SSR": safe_div(ssr_sum, n),
        "CPA": safe_div(cpa_sum, n),
        "CDFR": safe_div(cdfr_num, cdfr_den),
        "URFR": safe_div(urfr_sum, urfr_den),
        "PFR": safe_div(pfr_sum, n),
        "CPD": safe_div(cpd_sum, n),
        "clone_rate_drop": safe_div(o_sum - shuf_clone_sum, n),
    }


def bootstrap_metric_dict(
    arrays: dict[str, list[float]],
    metric_dict_fn: Callable[[dict[str, list[float]], list[int] | None], dict[str, float]],
    rng: random.Random,
    iters: int,
) -> dict[str, tuple[float, float, float]]:
    point = metric_dict_fn(arrays, None)
    n = len(next(iter(arrays.values())))
    if n == 0:
        return {key: (value, float("nan"), float("nan")) for key, value in point.items()}
    boot_values: dict[str, list[float]] = {key: [] for key in point}
    for _ in range(iters):
        indices = [rng.randrange(n) for _ in range(n)]
        sampled = metric_dict_fn(arrays, indices)
        for key, value in sampled.items():
            boot_values[key].append(value)
    return {
        key: (point[key], percentile(values, 0.025), percentile(values, 0.975))
        for key, values in boot_values.items()
    }


def bootstrap_metric_diff_dict(
    left_arrays: dict[str, list[float]],
    right_arrays: dict[str, list[float]],
    metric_dict_fn: Callable[[dict[str, list[float]], list[int] | None], dict[str, float]],
    rng: random.Random,
    iters: int,
) -> dict[str, tuple[float, float, float]]:
    left_point = metric_dict_fn(left_arrays, None)
    right_point = metric_dict_fn(right_arrays, None)
    point = {key: left_point[key] - right_point[key] for key in left_point}
    n = len(next(iter(left_arrays.values())))
    if n == 0:
        return {key: (value, float("nan"), float("nan")) for key, value in point.items()}
    boot_values: dict[str, list[float]] = {key: [] for key in point}
    for _ in range(iters):
        indices = [rng.randrange(n) for _ in range(n)]
        left_sample = metric_dict_fn(left_arrays, indices)
        right_sample = metric_dict_fn(right_arrays, indices)
        for key in point:
            boot_values[key].append(left_sample[key] - right_sample[key])
    return {
        key: (point[key], percentile(values, 0.025), percentile(values, 0.975))
        for key, values in boot_values.items()
    }


def build_original_bootstrap_rows(
    rows: list[dict[str, Any]],
    rng: random.Random,
    iters: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for (protocol, model), group in sorted(group_by(rows, "protocol", "model").items()):
        arrays = build_original_arrays(group)
        stats = bootstrap_metric_dict(arrays, original_metrics_from_arrays, rng, iters)
        for metric_name in ORIGINAL_METRICS:
            point, ci_low, ci_high = stats[metric_name]
            output.append(
                {
                    "protocol": protocol,
                    "model": model,
                    "metric": metric_name,
                    "point_estimate": point,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "n": len(group),
                }
            )
    return output


def build_counterfactual_bootstrap_rows(
    rows: list[dict[str, Any]],
    rng: random.Random,
    iters: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    grouped = group_by(rows, "protocol", "model", "variant")
    for (protocol, model, variant), group in sorted(grouped.items()):
        binary_proxy_count = sum(1 for row in group if row["counterfactual_uses_binary_proxy"])
        denom_cdfr = sum(1 for row in group if row["original_prediction_is_clone"])
        denom_urfr = sum(1 for row in group if not row["original_prediction_is_clone"])
        prob_mode_summary = summarise_prob_modes(group)
        arrays = build_counterfactual_arrays(group)
        stats = bootstrap_metric_dict(arrays, counterfactual_metrics_from_arrays, rng, iters)
        for metric_name in COUNTERFACTUAL_METRICS:
            point, ci_low, ci_high = stats[metric_name]
            output.append(
                {
                    "protocol": protocol,
                    "model": model,
                    "variant": variant,
                    "metric": metric_name,
                    "point_estimate": point,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "n": len(group),
                    "cdfr_denominator": denom_cdfr,
                    "urfr_denominator": denom_urfr,
                    "binary_proxy_rows": binary_proxy_count,
                    "probability_mode_summary": prob_mode_summary,
                }
            )
    return output


def build_original_model_mcnemar(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    grouped = group_by(rows, "protocol", "model")
    by_protocol: dict[str, dict[str, dict[str, dict[str, Any]]]] = defaultdict(dict)
    for (protocol, model), group in grouped.items():
        by_protocol[protocol][model] = {row["sample_id"]: row for row in group}

    for protocol, model_map in sorted(by_protocol.items()):
        for model_a, model_b in combinations(sorted(model_map), 2):
            shared_ids = sorted(set(model_map[model_a]) & set(model_map[model_b]))
            b = c = both_correct = both_wrong = 0
            for sample_id in shared_ids:
                a_correct = bool(model_map[model_a][sample_id]["correct"])
                b_correct = bool(model_map[model_b][sample_id]["correct"])
                if a_correct and not b_correct:
                    b += 1
                elif (not a_correct) and b_correct:
                    c += 1
                elif a_correct and b_correct:
                    both_correct += 1
                else:
                    both_wrong += 1
            output.append(
                {
                    "scope": "original_test",
                    "protocol": protocol,
                    "left": model_a,
                    "right": model_b,
                    "n_shared": len(shared_ids),
                    "left_only_correct": b,
                    "right_only_correct": c,
                    "both_correct": both_correct,
                    "both_wrong": both_wrong,
                    "p_value_exact": exact_mcnemar_pvalue(b, c),
                }
            )
    return output


def build_counterfactual_model_mcnemar(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    grouped = group_by(rows, "protocol", "variant", "model")
    by_scope: dict[tuple[str, str], dict[str, dict[str, dict[str, Any]]]] = defaultdict(dict)
    for (protocol, variant, model), group in grouped.items():
        by_scope[(protocol, variant)][model] = {row["sample_id"]: row for row in group}

    for (protocol, variant), model_map in sorted(by_scope.items()):
        for model_a, model_b in combinations(sorted(model_map), 2):
            shared_ids = sorted(set(model_map[model_a]) & set(model_map[model_b]))
            b = c = both_correct = both_wrong = 0
            for sample_id in shared_ids:
                a_correct = bool(model_map[model_a][sample_id]["shuffled_correct"])
                b_correct = bool(model_map[model_b][sample_id]["shuffled_correct"])
                if a_correct and not b_correct:
                    b += 1
                elif (not a_correct) and b_correct:
                    c += 1
                elif a_correct and b_correct:
                    both_correct += 1
                else:
                    both_wrong += 1
            output.append(
                {
                    "scope": "counterfactual_shuffled",
                    "protocol": protocol,
                    "variant": variant,
                    "left": model_a,
                    "right": model_b,
                    "n_shared": len(shared_ids),
                    "left_only_correct": b,
                    "right_only_correct": c,
                    "both_correct": both_correct,
                    "both_wrong": both_wrong,
                    "p_value_exact": exact_mcnemar_pvalue(b, c),
                }
            )
    return output


def build_b2_b3_mcnemar(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    by_group = group_by(rows, "protocol", "model", "variant")
    for (protocol, model, _variant) in sorted({(r["protocol"], r["model"], r["variant"]) for r in rows}):
        pass
    scopes = defaultdict(dict)
    for (protocol, model, variant), group in by_group.items():
        scopes[(protocol, model)][variant] = {row["sample_id"]: row for row in group}

    for (protocol, model), variant_map in sorted(scopes.items()):
        if "b2" not in variant_map or "b3" not in variant_map:
            continue
        shared_ids = sorted(set(variant_map["b2"]) & set(variant_map["b3"]))
        b = c = both_correct = both_wrong = 0
        for sample_id in shared_ids:
            b2_correct = bool(variant_map["b2"][sample_id]["shuffled_correct"])
            b3_correct = bool(variant_map["b3"][sample_id]["shuffled_correct"])
            if b2_correct and not b3_correct:
                b += 1
            elif (not b2_correct) and b3_correct:
                c += 1
            elif b2_correct and b3_correct:
                both_correct += 1
            else:
                both_wrong += 1
        output.append(
            {
                "scope": "b2_vs_b3_shuffled",
                "protocol": protocol,
                "model": model,
                "left": "b2",
                "right": "b3",
                "n_shared": len(shared_ids),
                "left_only_correct": b,
                "right_only_correct": c,
                "both_correct": both_correct,
                "both_wrong": both_wrong,
                "p_value_exact": exact_mcnemar_pvalue(b, c),
            }
        )
    return output


def build_variant_diff_bootstrap(
    rows: list[dict[str, Any]],
    rng: random.Random,
    iters: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    grouped = group_by(rows, "protocol", "model", "variant")
    scopes = defaultdict(dict)
    for (protocol, model, variant), group in grouped.items():
        scopes[(protocol, model)][variant] = {row["sample_id"]: row for row in group}

    for (protocol, model), variant_map in sorted(scopes.items()):
        if "b2" not in variant_map or "b3" not in variant_map:
            continue
        shared_ids = sorted(set(variant_map["b2"]) & set(variant_map["b3"]))
        left_rows = [variant_map["b2"][sample_id] for sample_id in shared_ids]
        right_rows = [variant_map["b3"][sample_id] for sample_id in shared_ids]
        stats = bootstrap_metric_diff_dict(
            build_counterfactual_arrays(left_rows),
            build_counterfactual_arrays(right_rows),
            counterfactual_metrics_from_arrays,
            rng,
            iters,
        )
        for metric_name in COUNTERFACTUAL_METRICS:
            point, ci_low, ci_high = stats[metric_name]
            output.append(
                {
                    "comparison": "b2_minus_b3",
                    "protocol": protocol,
                    "model": model,
                    "metric": metric_name,
                    "point_estimate": point,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "n_shared": len(shared_ids),
                }
            )
    return output


def build_model_diff_bootstrap(
    rows: list[dict[str, Any]],
    rng: random.Random,
    iters: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    grouped = group_by(rows, "protocol", "variant", "model")
    scopes: dict[tuple[str, str], dict[str, dict[str, dict[str, Any]]]] = defaultdict(dict)
    for (protocol, variant, model), group in grouped.items():
        scopes[(protocol, variant)][model] = {row["sample_id"]: row for row in group}

    for (protocol, variant), model_map in sorted(scopes.items()):
        for left, right in combinations(sorted(model_map), 2):
            shared_ids = sorted(set(model_map[left]) & set(model_map[right]))
            left_rows = [model_map[left][sample_id] for sample_id in shared_ids]
            right_rows = [model_map[right][sample_id] for sample_id in shared_ids]
            stats = bootstrap_metric_diff_dict(
                build_counterfactual_arrays(left_rows),
                build_counterfactual_arrays(right_rows),
                counterfactual_metrics_from_arrays,
                rng,
                iters,
            )
            for metric_name in COUNTERFACTUAL_METRICS:
                point, ci_low, ci_high = stats[metric_name]
                output.append(
                    {
                        "comparison": "model_left_minus_right",
                        "protocol": protocol,
                        "variant": variant,
                        "left": left,
                        "right": right,
                        "metric": metric_name,
                        "point_estimate": point,
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                        "n_shared": len(shared_ids),
                    }
                )
    return output


def build_summary_markdown(
    original_bootstrap: list[dict[str, Any]],
    counterfactual_bootstrap: list[dict[str, Any]],
    mcnemar_rows: list[dict[str, Any]],
) -> str:
    lines = [
        "# Third-Round Paired Statistics Summary (2026-06-26)",
        "",
        "## What Was Generated",
        "",
        "- Sample-level exports for original test predictions and paired counterfactual predictions.",
        "- Bootstrap 95% confidence intervals for original test metrics and counterfactual dependency metrics.",
        "- Exact McNemar tests for model-vs-model comparisons and B2-vs-B3 comparisons.",
        "",
        "## Notes",
        "",
        "- `CPA`, `CDFR`, `SSR`, `PFR`, `CPD`, and `clone_rate_drop` are computed from paired sample-level rows.",
        "- `DeepSeek-v4-flash` lacks native probability outputs in these saved predictions, so its `CPD` uses a `binary_proxy` scale (`yes=1`, `no=0`).",
        "",
        "## Counterfactual CI Snapshot",
        "",
    ]

    snapshot_rows = [
        row
        for row in counterfactual_bootstrap
        if row["metric"] in {"CPA", "CDFR", "SSR", "CPD"}
    ]
    snapshot_rows = sorted(
        snapshot_rows,
        key=lambda row: (row["protocol"], row["model"], row["variant"], row["metric"]),
    )
    lines.append("| Protocol | Model | Variant | Metric | Point | 95% CI |")
    lines.append("|---|---|---|---|---:|---|")
    for row in snapshot_rows:
        lines.append(
            "| {protocol} | {model} | {variant} | {metric} | {point:.4f} | [{low:.4f}, {high:.4f}] |".format(
                protocol=row["protocol"],
                model=row["model"],
                variant=row["variant"],
                metric=row["metric"],
                point=row["point_estimate"],
                low=row["ci_low"],
                high=row["ci_high"],
            )
        )

    lines.extend(
        [
            "",
            "## McNemar Snapshot",
            "",
            "| Scope | Protocol | Variant/Model | Left | Right | Discordant (L only / R only) | p-value |",
            "|---|---|---|---|---|---|---:|",
        ]
    )

    for row in mcnemar_rows[:24]:
        lines.append(
            "| {scope} | {protocol} | {variant_model} | {left} | {right} | {b} / {c} | {p:.6f} |".format(
                scope=row["scope"],
                protocol=row.get("protocol", "-"),
                variant_model=row.get("variant", row.get("model", "-")),
                left=row["left"],
                right=row["right"],
                b=row["left_only_correct"],
                c=row["right_only_correct"],
                p=row["p_value_exact"],
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    rng = random.Random(args.seed)

    original_path = input_dir / "third_round_original_full_sample_predictions_20260626.jsonl"
    paired_path = input_dir / "third_round_paired_counterfactual_predictions_20260626.jsonl"

    original_rows = load_jsonl(original_path)
    paired_rows = load_jsonl(paired_path)

    original_bootstrap = build_original_bootstrap_rows(original_rows, rng, args.bootstrap_iters)
    counterfactual_bootstrap = build_counterfactual_bootstrap_rows(
        paired_rows,
        rng,
        args.bootstrap_iters,
    )
    original_mcnemar = build_original_model_mcnemar(original_rows)
    counterfactual_mcnemar = build_counterfactual_model_mcnemar(paired_rows)
    b2_b3_mcnemar = build_b2_b3_mcnemar(paired_rows)
    variant_diff_bootstrap = build_variant_diff_bootstrap(
        paired_rows,
        rng,
        args.bootstrap_iters,
    )
    model_diff_bootstrap = build_model_diff_bootstrap(
        paired_rows,
        rng,
        args.bootstrap_iters,
    )

    original_bootstrap_path = input_dir / "third_round_original_test_bootstrap_ci_20260626.csv"
    counterfactual_bootstrap_path = input_dir / "third_round_counterfactual_bootstrap_ci_20260626.csv"
    mcnemar_path = input_dir / "third_round_mcnemar_tests_20260626.csv"
    variant_diff_path = input_dir / "third_round_variant_diff_bootstrap_ci_20260626.csv"
    model_diff_path = input_dir / "third_round_model_diff_bootstrap_ci_20260626.csv"
    summary_path = input_dir / "third_round_paired_statistics_summary_20260626.md"
    manifest_path = input_dir / "third_round_paired_statistics_manifest_20260626.json"

    write_csv(original_bootstrap_path, original_bootstrap)
    write_csv(counterfactual_bootstrap_path, counterfactual_bootstrap)
    write_csv(mcnemar_path, original_mcnemar + counterfactual_mcnemar + b2_b3_mcnemar)
    write_csv(variant_diff_path, variant_diff_bootstrap)
    write_csv(model_diff_path, model_diff_bootstrap)
    summary_path.write_text(
        build_summary_markdown(
            original_bootstrap=original_bootstrap,
            counterfactual_bootstrap=counterfactual_bootstrap,
            mcnemar_rows=original_mcnemar + counterfactual_mcnemar + b2_b3_mcnemar,
        ),
        encoding="utf-8",
    )
    manifest_path.write_text(
        json.dumps(
            {
                "input_dir": str(input_dir),
                "bootstrap_iters": args.bootstrap_iters,
                "seed": args.seed,
                "inputs": {
                    "original_jsonl": str(original_path),
                    "paired_jsonl": str(paired_path),
                },
                "outputs": {
                    "original_bootstrap_csv": str(original_bootstrap_path),
                    "counterfactual_bootstrap_csv": str(counterfactual_bootstrap_path),
                    "mcnemar_csv": str(mcnemar_path),
                    "variant_diff_bootstrap_csv": str(variant_diff_path),
                    "model_diff_bootstrap_csv": str(model_diff_path),
                    "summary_md": str(summary_path),
                },
                "n_original_rows": len(original_rows),
                "n_paired_rows": len(paired_rows),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "input_dir": str(input_dir),
                "n_original_rows": len(original_rows),
                "n_paired_rows": len(paired_rows),
                "bootstrap_iters": args.bootstrap_iters,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
