#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z_]\w*|\d+|[^\s]")

FEATURE_GROUPS = {
    "length": {
        "char_a",
        "char_b",
        "line_a",
        "line_b",
        "token_a",
        "token_b",
        "id_a",
        "id_b",
        "char_abs_diff",
        "line_abs_diff",
        "token_abs_diff",
        "id_abs_diff",
        "char_ratio_ab",
        "char_ratio_ba",
        "line_ratio_ab",
        "line_ratio_ba",
        "token_ratio_ab",
        "token_ratio_ba",
        "id_ratio_ab",
        "id_ratio_ba",
    },
    "language": {"lang_pair"},
    "identifier": {
        "id_a",
        "id_b",
        "id_abs_diff",
        "id_ratio_ab",
        "id_ratio_ba",
        "identifier_set_jaccard",
        "identifier_multiset_overlap",
        "identifier_multiset_l1",
    },
    "token": {
        "token_a",
        "token_b",
        "token_abs_diff",
        "token_ratio_ab",
        "token_ratio_ba",
        "token_set_jaccard",
        "token_multiset_overlap",
        "token_multiset_l1",
        "line_density_a",
        "line_density_b",
    },
    "structure": {
        "structure_multiset_overlap",
        "structure_multiset_l1",
    },
    "complexity": {
        "line_density_a",
        "line_density_b",
        "char_ratio_ab",
        "char_ratio_ba",
        "line_ratio_ab",
        "line_ratio_ba",
        "token_ratio_ab",
        "token_ratio_ba",
        "id_ratio_ab",
        "id_ratio_ba",
    },
}


@dataclass
class Example:
    pair_id: str
    label: int
    lang_a: str
    lang_b: str
    problem_id_a: str
    problem_id_b: str
    code_a: str
    code_b: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run A4-full feature-group ablations.")
    parser.add_argument("--split-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--c-grid", nargs="+", type=float, default=(0.1, 1.0, 10.0))
    parser.add_argument("--permutation-repeats", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_rows(path: Path) -> list[Example]:
    rows: list[Example] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            rows.append(
                Example(
                    pair_id=payload["split_pair_id"],
                    label=1 if payload["type"] == "clone" else 0,
                    lang_a=payload["ll1"],
                    lang_b=payload["ll2"],
                    problem_id_a=payload["problem_id_1"],
                    problem_id_b=payload["problem_id_2"],
                    code_a=payload["codeA"],
                    code_b=payload["codeB"],
                )
            )
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


def count_nonempty_lines(code: str) -> int:
    return sum(1 for line in code.splitlines() if line.strip())


def count_tokens(code: str) -> int:
    return len(TOKEN_RE.findall(code))


def safe_ratio(left: float, right: float) -> float:
    return float(left) / float(max(right, 1e-6))


def identifier_tokens(code: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(code) if re.match(r"[A-Za-z_]\w*$", token)]


def jaccard(items_left: list[str], items_right: list[str]) -> float:
    set_left = set(items_left)
    set_right = set(items_right)
    union = set_left | set_right
    if not union:
        return 0.0
    return len(set_left & set_right) / len(union)


def numeric_overlap(left: Counter, right: Counter) -> tuple[float, float]:
    keys = set(left) | set(right)
    if not keys:
        return 0.0, 0.0
    shared = sum(min(left.get(key, 0), right.get(key, 0)) for key in keys)
    total = sum(max(left.get(key, 0), right.get(key, 0)) for key in keys)
    l1 = sum(abs(left.get(key, 0) - right.get(key, 0)) for key in keys)
    return (shared / total if total else 0.0, float(l1))


def structure_counter(code: str) -> Counter:
    counter = Counter()
    lowered = code.lower()
    for marker in ("{", "}", "(", ")", "[", "]", ",", ".", ";", ":"):
        counter[marker] = code.count(marker)
    for keyword in ("if", "else", "for", "while", "switch", "case", "return", "class", "def", "fn"):
        counter[keyword] = len(re.findall(rf"\b{keyword}\b", lowered))
    return counter


def full_surface_feature_dict(row: Example) -> dict[str, float | str]:
    tokens_a = TOKEN_RE.findall(row.code_a)
    tokens_b = TOKEN_RE.findall(row.code_b)
    ids_a = identifier_tokens(row.code_a)
    ids_b = identifier_tokens(row.code_b)
    struct_a = structure_counter(row.code_a)
    struct_b = structure_counter(row.code_b)
    struct_overlap, struct_l1 = numeric_overlap(struct_a, struct_b)
    token_overlap, token_l1 = numeric_overlap(Counter(token.lower() for token in tokens_a), Counter(token.lower() for token in tokens_b))
    id_overlap, id_l1 = numeric_overlap(Counter(ids_a), Counter(ids_b))
    line_a = count_nonempty_lines(row.code_a)
    line_b = count_nonempty_lines(row.code_b)
    char_a = len(row.code_a)
    char_b = len(row.code_b)
    return {
        "lang_pair": f"{row.lang_a}->{row.lang_b}",
        "char_a": float(char_a),
        "char_b": float(char_b),
        "line_a": float(line_a),
        "line_b": float(line_b),
        "token_a": float(len(tokens_a)),
        "token_b": float(len(tokens_b)),
        "id_a": float(len(ids_a)),
        "id_b": float(len(ids_b)),
        "char_abs_diff": float(abs(char_a - char_b)),
        "line_abs_diff": float(abs(line_a - line_b)),
        "token_abs_diff": float(abs(len(tokens_a) - len(tokens_b))),
        "id_abs_diff": float(abs(len(ids_a) - len(ids_b))),
        "char_ratio_ab": safe_ratio(char_a, char_b),
        "char_ratio_ba": safe_ratio(char_b, char_a),
        "line_ratio_ab": safe_ratio(line_a, line_b),
        "line_ratio_ba": safe_ratio(line_b, line_a),
        "token_ratio_ab": safe_ratio(len(tokens_a), len(tokens_b)),
        "token_ratio_ba": safe_ratio(len(tokens_b), len(tokens_a)),
        "id_ratio_ab": safe_ratio(len(ids_a), len(ids_b)),
        "id_ratio_ba": safe_ratio(len(ids_b), len(ids_a)),
        "token_set_jaccard": jaccard([token.lower() for token in tokens_a], [token.lower() for token in tokens_b]),
        "identifier_set_jaccard": jaccard(ids_a, ids_b),
        "token_multiset_overlap": token_overlap,
        "identifier_multiset_overlap": id_overlap,
        "structure_multiset_overlap": struct_overlap,
        "token_multiset_l1": token_l1,
        "identifier_multiset_l1": id_l1,
        "structure_multiset_l1": struct_l1,
        "line_density_a": safe_ratio(len(tokens_a), max(line_a, 1)),
        "line_density_b": safe_ratio(len(tokens_b), max(line_b, 1)),
    }


def compute_metrics(gold: list[int], pred: list[int], prob_yes: list[float] | None = None) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    for g, p in zip(gold, pred):
        if g == 1 and p == 1:
            tp += 1
        elif g == 0 and p == 1:
            fp += 1
        elif g == 0 and p == 0:
            tn += 1
        else:
            fn += 1
    precision_pos = tp / (tp + fp) if (tp + fp) else 0.0
    recall_pos = tp / (tp + fn) if (tp + fn) else 0.0
    precision_neg = tn / (tn + fn) if (tn + fn) else 0.0
    recall_neg = tn / (tn + fp) if (tn + fp) else 0.0
    f1_pos = 2 * precision_pos * recall_pos / (precision_pos + recall_pos) if (precision_pos + recall_pos) else 0.0
    f1_neg = 2 * precision_neg * recall_neg / (precision_neg + recall_neg) if (precision_neg + recall_neg) else 0.0
    accuracy = (tp + tn) / max(tp + tn + fp + fn, 1)
    balanced_accuracy = (recall_pos + recall_neg) / 2.0
    metrics = {
        "n": len(gold),
        "precision": round(precision_pos, 4),
        "recall": round(recall_pos, 4),
        "f1": round(f1_pos, 4),
        "macro_f1": round((f1_pos + f1_neg) / 2.0, 4),
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(balanced_accuracy, 4),
        "predicted_positive_rate": round(sum(pred) / max(len(pred), 1), 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }
    if prob_yes is not None and len(set(gold)) > 1:
        try:
            from sklearn.metrics import roc_auc_score
            metrics["auroc"] = round(float(roc_auc_score(gold, prob_yes)), 4)
        except Exception:
            metrics["auroc"] = None
    else:
        metrics["auroc"] = None
    return metrics


def group_feature_names(group: str, all_feature_names: list[str]) -> list[str]:
    if group == "full":
        return list(all_feature_names)
    allowed = FEATURE_GROUPS[group]
    selected = []
    for name in all_feature_names:
        if name.startswith("lang_pair="):
            if "lang_pair" in allowed:
                selected.append(name)
        elif name in allowed:
            selected.append(name)
    return selected


def get_column_indices(feature_names: list[str], selected_names: list[str]) -> list[int]:
    wanted = set(selected_names)
    return [idx for idx, name in enumerate(feature_names) if name in wanted]


def fit_and_eval_group(
    group_name: str,
    feature_names: list[str],
    x_train,
    y_train,
    x_valid,
    y_valid,
    x_test,
    y_test,
    c_grid: list[float],
):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    selected_names = group_feature_names(group_name, feature_names)
    selected_indices = get_column_indices(feature_names, selected_names)
    if not selected_indices:
        raise ValueError(f"No features selected for group {group_name}")

    x_train_sub = x_train[:, selected_indices]
    x_valid_sub = x_valid[:, selected_indices]
    x_test_sub = x_test[:, selected_indices]

    scaler = StandardScaler(with_mean=False)
    x_train_scaled = scaler.fit_transform(x_train_sub)
    x_valid_scaled = scaler.transform(x_valid_sub)
    x_test_scaled = scaler.transform(x_test_sub)

    best_model = None
    best_c = None
    best_valid_metrics = None
    best_key = None
    for c_value in c_grid:
        model = LogisticRegression(C=c_value, solver="liblinear", max_iter=1000, random_state=42)
        model.fit(x_train_scaled, y_train)
        valid_pred = model.predict(x_valid_scaled).tolist()
        valid_prob = model.predict_proba(x_valid_scaled)[:, 1].tolist()
        valid_metrics = compute_metrics(y_valid.tolist(), valid_pred, valid_prob)
        ranking = (valid_metrics["balanced_accuracy"], valid_metrics["macro_f1"], -c_value)
        if best_key is None or ranking > best_key:
            best_key = ranking
            best_model = model
            best_c = c_value
            best_valid_metrics = valid_metrics
    assert best_model is not None

    test_pred = best_model.predict(x_test_scaled).tolist()
    test_prob = best_model.predict_proba(x_test_scaled)[:, 1].tolist()
    test_metrics = compute_metrics(y_test.tolist(), test_pred, test_prob)
    coef = best_model.coef_[0]
    coef_rows = []
    for idx, coef_value in enumerate(coef):
        coef_rows.append(
            {
                "feature_group": group_name,
                "feature_name": selected_names[idx],
                "coefficient": float(coef_value),
                "abs_coefficient": abs(float(coef_value)),
            }
        )
    coef_rows.sort(key=lambda row: row["abs_coefficient"], reverse=True)
    sample_predictions = []
    for pred_idx, (pred_label, prob_yes) in enumerate(zip(test_pred, test_prob)):
        sample_predictions.append(
            {
                "feature_group": group_name,
                "pair_id": pred_idx,
                "prediction_text": "yes" if int(pred_label) == 1 else "no",
                "prob_yes": round(float(prob_yes), 6),
            }
        )
    return {
        "group_name": group_name,
        "selected_c": best_c,
        "selected_feature_names": selected_names,
        "selected_feature_dim": len(selected_names),
        "valid_metrics": best_valid_metrics,
        "test_metrics": test_metrics,
        "coef_rows": coef_rows,
        "model": best_model,
        "scaler": scaler,
        "selected_indices": selected_indices,
        "x_test_scaled": x_test_scaled,
        "test_pred": test_pred,
        "test_prob": test_prob,
    }


def permutation_importance_rows(
    model,
    x_test_scaled,
    y_test,
    feature_names: list[str],
    repeats: int,
    seed: int,
) -> list[dict[str, Any]]:
    from sklearn.inspection import permutation_importance

    if hasattr(x_test_scaled, "toarray"):
        x_eval = x_test_scaled.toarray()
    else:
        x_eval = x_test_scaled

    result = permutation_importance(
        model,
        x_eval,
        y_test,
        scoring="balanced_accuracy",
        n_repeats=repeats,
        random_state=seed,
    )
    rows = []
    for idx, name in enumerate(feature_names):
        rows.append(
            {
                "feature_name": name,
                "importance_mean": float(result.importances_mean[idx]),
                "importance_std": float(result.importances_std[idx]),
            }
        )
    rows.sort(key=lambda row: row["importance_mean"], reverse=True)
    return rows


def per_language_rows(examples: list[Example], y_pred: list[int], y_prob: list[float], group_name: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for idx, ex in enumerate(examples):
        grouped[f"{ex.lang_a}->{ex.lang_b}"].append(idx)
    rows = []
    for lang_pair, indices in sorted(grouped.items()):
        gold = [examples[idx].label for idx in indices]
        pred = [y_pred[idx] for idx in indices]
        prob = [y_prob[idx] for idx in indices]
        metrics = compute_metrics(gold, pred, prob)
        rows.append(
            {
                "feature_group": group_name,
                "lang_pair": lang_pair,
                **metrics,
            }
        )
    return rows


def distribution_summary_rows(examples: list[Example], feature_dicts: list[dict[str, float | str]]) -> list[dict[str, Any]]:
    numeric_keys = [key for key, value in feature_dicts[0].items() if isinstance(value, (int, float))]
    rows = []
    by_label = defaultdict(list)
    for ex, feats in zip(examples, feature_dicts):
        by_label[ex.label].append(feats)
    pos_rows = by_label[1]
    neg_rows = by_label[0]
    for key in numeric_keys:
        pos_values = [float(row[key]) for row in pos_rows]
        neg_values = [float(row[key]) for row in neg_rows]
        pos_mean = sum(pos_values) / max(len(pos_values), 1)
        neg_mean = sum(neg_values) / max(len(neg_values), 1)
        rows.append(
            {
                "feature_name": key,
                "positive_mean": pos_mean,
                "negative_mean": neg_mean,
                "mean_diff": pos_mean - neg_mean,
                "positive_median": sorted(pos_values)[len(pos_values) // 2] if pos_values else None,
                "negative_median": sorted(neg_values)[len(neg_values) // 2] if neg_values else None,
            }
        )
    rows.sort(key=lambda row: abs(row["mean_diff"]), reverse=True)
    return rows


def render_summary(protocol_results: list[dict[str, Any]]) -> str:
    lines = [
        "# A4-full Feature Group Summary",
        "",
        "This report decomposes the original `A4-full` lexical/surface baseline into interpretable feature groups under the same clean-split protocol and logistic classifier family.",
        "",
    ]
    for result in protocol_results:
        protocol = result["protocol"]
        lines.extend([f"## {protocol}", ""])
        lines.append("| Feature Group | F1 | Balanced Acc. | AUROC | Precision | Recall | Selected C | Dim |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for row in result["ablation_rows"]:
            lines.append(
                f"| {row['feature_group']} | {row['f1']:.4f} | {row['balanced_accuracy']:.4f} | "
                f"{row['auroc'] if row['auroc'] is not None else '-'} | {row['precision']:.4f} | {row['recall']:.4f} | "
                f"{row['selected_c']} | {row['feature_dim']} |"
            )
        lines.extend(["", "Top coefficient features from `full`:", ""])
        for row in result["coef_rows"][:10]:
            lines.append(f"- `{row['feature_name']}`: coef={row['coefficient']:.4f}")
        lines.extend(["", "Top permutation features from `full`:", ""])
        for row in result["perm_rows"][:10]:
            lines.append(
                f"- `{row['feature_name']}`: importance={float(row['importance_mean']):.6f} ± {float(row['importance_std']):.6f}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    split_dir = Path(args.split_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
        from sklearn.feature_extraction import DictVectorizer
    except ModuleNotFoundError as exc:
        raise SystemExit("run_a4_full_feature_ablation.py requires numpy and scikit-learn.") from exc

    train_rows = load_rows(split_dir / "train.jsonl")
    valid_rows = load_rows(split_dir / "valid.jsonl")
    test_rows = load_rows(split_dir / "test.jsonl")

    train_dicts = [full_surface_feature_dict(row) for row in train_rows]
    valid_dicts = [full_surface_feature_dict(row) for row in valid_rows]
    test_dicts = [full_surface_feature_dict(row) for row in test_rows]

    vectorizer = DictVectorizer(sparse=True)
    x_train = vectorizer.fit_transform(train_dicts)
    x_valid = vectorizer.transform(valid_dicts)
    x_test = vectorizer.transform(test_dicts)
    y_train = np.array([row.label for row in train_rows], dtype="int64")
    y_valid = np.array([row.label for row in valid_rows], dtype="int64")
    y_test = np.array([row.label for row in test_rows], dtype="int64")
    feature_names = vectorizer.get_feature_names_out().tolist()

    protocol = split_dir.name
    ablation_rows = []
    coef_rows = []
    per_lang_rows = []
    artifact_manifest = {
        "protocol": protocol,
        "split_dir": str(split_dir),
        "output_dir": str(output_dir),
        "feature_groups": {},
    }

    for group_name in ["length", "language", "identifier", "token", "structure", "complexity", "full"]:
        fitted = fit_and_eval_group(
            group_name=group_name,
            feature_names=feature_names,
            x_train=x_train,
            y_train=y_train,
            x_valid=x_valid,
            y_valid=y_valid,
            x_test=x_test,
            y_test=y_test,
            c_grid=list(args.c_grid),
        )
        metrics = fitted["test_metrics"]
        ablation_rows.append(
            {
                "protocol": protocol,
                "feature_group": group_name,
                "selected_c": fitted["selected_c"],
                "feature_dim": fitted["selected_feature_dim"],
                **metrics,
            }
        )
        for row in fitted["coef_rows"]:
            coef_rows.append({"protocol": protocol, **row})
        per_lang_rows.extend(
            {"protocol": protocol, **row}
            for row in per_language_rows(test_rows, fitted["test_pred"], fitted["test_prob"], group_name)
        )

        group_dir = output_dir / group_name
        write_json(
            group_dir / "metrics.json",
            {
                "protocol": protocol,
                "feature_group": group_name,
                "selected_c": fitted["selected_c"],
                "feature_dim": fitted["selected_feature_dim"],
                "selected_feature_names": fitted["selected_feature_names"],
                "valid_metrics": fitted["valid_metrics"],
                "test_metrics": metrics,
            },
        )
        artifact_manifest["feature_groups"][group_name] = {
            "selected_c": fitted["selected_c"],
            "feature_dim": fitted["selected_feature_dim"],
            "metrics_path": str(group_dir / "metrics.json"),
        }

        if group_name == "full":
            perm_rows = permutation_importance_rows(
                fitted["model"],
                fitted["x_test_scaled"],
                y_test,
                fitted["selected_feature_names"],
                repeats=args.permutation_repeats,
                seed=args.seed,
            )
            distribution_rows = distribution_summary_rows(test_rows, test_dicts)
            write_csv(output_dir / "a4_permutation_importance.csv", [{"protocol": protocol, **row} for row in perm_rows])
            write_csv(output_dir / "a4_feature_distribution_summary.csv", [{"protocol": protocol, **row} for row in distribution_rows])
            artifact_manifest["full_group"] = {
                "permutation_importance_path": str(output_dir / "a4_permutation_importance.csv"),
                "distribution_summary_path": str(output_dir / "a4_feature_distribution_summary.csv"),
            }

    write_csv(output_dir / "a4_feature_group_ablation_results.csv", ablation_rows)
    write_csv(output_dir / "a4_coefficient_ranking.csv", coef_rows)
    write_csv(output_dir / "a4_per_language_pair_results.csv", per_lang_rows)
    write_json(output_dir / "a4_feature_group_manifest.json", artifact_manifest)

    full_perm_rows = list(csv.DictReader((output_dir / "a4_permutation_importance.csv").open(encoding="utf-8")))
    summary = render_summary(
        [
            {
                "protocol": protocol,
                "ablation_rows": ablation_rows,
                "coef_rows": coef_rows,
                "perm_rows": full_perm_rows,
            }
        ]
    )
    (output_dir / "a4_feature_group_summary.md").write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
