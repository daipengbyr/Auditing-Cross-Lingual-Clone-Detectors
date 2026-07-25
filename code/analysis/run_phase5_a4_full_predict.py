#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from run_a4_full_feature_ablation import full_surface_feature_dict


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
    parser = argparse.ArgumentParser(description="Train A4-full on a split and predict arbitrary Phase 5 JSONL inputs.")
    parser.add_argument("--split-dir", type=Path, required=True)
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--experiment-name", default="a4_full_surface_lexical_phase5")
    parser.add_argument("--c-grid", nargs="+", type=float, default=(0.1, 1.0, 10.0))
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_split_examples(path: Path) -> list[Example]:
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


def load_variant_examples(path: Path) -> list[Example]:
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


def choose_model(train_rows: list[Example], valid_rows: list[Example], c_grid: list[float], seed: int):
    import numpy as np
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    train_features = [full_surface_feature_dict(row) for row in train_rows]
    valid_features = [full_surface_feature_dict(row) for row in valid_rows]
    y_train = np.array([row.label for row in train_rows], dtype=int)
    y_valid = np.array([row.label for row in valid_rows], dtype=int)

    vectorizer = DictVectorizer(sparse=True)
    x_train = vectorizer.fit_transform(train_features)
    x_valid = vectorizer.transform(valid_features)

    scaler = StandardScaler(with_mean=False)
    x_train_scaled = scaler.fit_transform(x_train)
    x_valid_scaled = scaler.transform(x_valid)

    best_model = None
    best_c = None
    best_key = None
    for c_value in c_grid:
        model = LogisticRegression(C=c_value, solver="liblinear", max_iter=1000, random_state=seed)
        model.fit(x_train_scaled, y_train)
        valid_pred = model.predict(x_valid_scaled)
        tp = int(((y_valid == 1) & (valid_pred == 1)).sum())
        fp = int(((y_valid == 0) & (valid_pred == 1)).sum())
        tn = int(((y_valid == 0) & (valid_pred == 0)).sum())
        fn = int(((y_valid == 1) & (valid_pred == 0)).sum())
        recall_pos = tp / (tp + fn) if (tp + fn) else 0.0
        recall_neg = tn / (tn + fp) if (tn + fp) else 0.0
        precision_pos = tp / (tp + fp) if (tp + fp) else 0.0
        f1_pos = 2 * precision_pos * recall_pos / (precision_pos + recall_pos) if (precision_pos + recall_pos) else 0.0
        precision_neg = tn / (tn + fn) if (tn + fn) else 0.0
        f1_neg = 2 * precision_neg * recall_neg / (precision_neg + recall_neg) if (precision_neg + recall_neg) else 0.0
        balanced_accuracy = (recall_pos + recall_neg) / 2.0
        macro_f1 = (f1_pos + f1_neg) / 2.0
        ranking = (balanced_accuracy, macro_f1, -c_value)
        if best_key is None or ranking > best_key:
            best_key = ranking
            best_model = model
            best_c = c_value

    assert best_model is not None and best_c is not None
    return vectorizer, scaler, best_model, best_c


def predict_rows(
    rows: list[Example],
    *,
    vectorizer,
    scaler,
    model,
    selected_c: float,
    experiment_name: str,
) -> list[dict]:
    features = [full_surface_feature_dict(row) for row in rows]
    x_eval = scaler.transform(vectorizer.transform(features))
    pred = model.predict(x_eval).tolist()
    prob_yes = model.predict_proba(x_eval)[:, 1].tolist()
    output_rows = []
    for row, pred_label, prob in zip(rows, pred, prob_yes):
        confidence = float(prob if int(pred_label) == 1 else 1.0 - prob)
        output_rows.append(
            {
                "pair_id": row.pair_id,
                "label": row.label,
                "lang_a": row.lang_a,
                "lang_b": row.lang_b,
                "problem_id_a": row.problem_id_a,
                "problem_id_b": row.problem_id_b,
                "prediction_text": "yes" if int(pred_label) == 1 else "no",
                "confidence": round(confidence, 6),
                "prob_yes": round(float(prob), 6),
                "meta": {
                    "experiment": experiment_name,
                    "selected_c": float(selected_c),
                },
            }
        )
    return output_rows


def main() -> None:
    args = parse_args()

    train_rows = load_split_examples(args.split_dir / "train.jsonl")
    valid_rows = load_split_examples(args.split_dir / "valid.jsonl")
    variant_rows = load_variant_examples(args.input_jsonl)

    vectorizer, scaler, model, selected_c = choose_model(train_rows, valid_rows, list(args.c_grid), args.seed)
    predictions = predict_rows(
        variant_rows,
        vectorizer=vectorizer,
        scaler=scaler,
        model=model,
        selected_c=selected_c,
        experiment_name=args.experiment_name,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(predictions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "n_predictions": len(predictions),
                "selected_c": selected_c,
                "experiment_name": args.experiment_name,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
