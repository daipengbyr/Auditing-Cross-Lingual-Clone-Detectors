#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MIRROR_ROOT = ROOT / "outputs" / "third_round_remote_mirror_20260626"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "third_round_deepseek_prompt_ablation_20260626"

API_URL = "https://api.deepseek.com/chat/completions"

PROMPTS = {
    "label_only": {
        "system": (
            "You are a careful evaluator for cross-language code clone detection. "
            "Given two code snippets, decide whether they implement the same core functionality "
            "regardless of programming language. Return exactly one JSON object and no other text. "
            'The JSON must be either {"label":"yes"} or {"label":"no"}.'
        ),
        "user_template": (
            "Determine whether the following two code snippets are semantic clones.\n"
            "Consider semantics and program behavior, not syntax alone.\n\n"
            "Code A ({lang_a}):\n```{code_a}```\n\n"
            "Code B ({lang_b}):\n```{code_b}```\n\n"
            'Return exactly one JSON object and no other text:\n{{"label":"yes"}}\nor\n{{"label":"no"}}'
        ),
    },
    "evidence_guided": {
        "system": (
            "You are a careful evaluator for cross-language code clone detection. "
            "Compare input/output behavior, control flow, state updates, and core algorithm. "
            "Be willing to predict yes when the implementation strategy is semantically aligned "
            "even if syntax and language constructs differ. Return exactly one JSON object and no other text. "
            'The JSON must be either {"label":"yes"} or {"label":"no"}.'
        ),
        "user_template": (
            "Decide whether these two programs are semantic clones.\n"
            "Before deciding, compare the following internally: input contract, output contract, "
            "main loop/recurrence, state updates, and edge-case handling. Do not output the analysis.\n\n"
            "Code A ({lang_a}):\n```{code_a}```\n\n"
            "Code B ({lang_b}):\n```{code_b}```\n\n"
            'Return exactly one JSON object and no other text:\n{{"label":"yes"}}\nor\n{{"label":"no"}}'
        ),
    },
    "conservative_off": {
        "system": (
            "You are a careful evaluator for cross-language code clone detection. "
            "Do not require near-identical structure. If two snippets solve the same task with the same core logic "
            "and produce the same outputs for the same inputs, predict yes even when decomposition, helpers, "
            "or surface forms differ. Return exactly one JSON object and no other text. "
            'The JSON must be either {"label":"yes"} or {"label":"no"}.'
        ),
        "user_template": (
            "Determine whether the following two code snippets are semantic clones.\n"
            "Use a permissive semantic criterion: implementation details may differ, but the core behavior must match.\n\n"
            "Code A ({lang_a}):\n```{code_a}```\n\n"
            "Code B ({lang_b}):\n```{code_b}```\n\n"
            'Return exactly one JSON object and no other text:\n{{"label":"yes"}}\nor\n{{"label":"no"}}'
        ),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DeepSeek prompt ablation on P2.")
    parser.add_argument("--api-key-env", default="DEEPSEEK_API_KEY")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--mirror-root", type=Path, default=DEFAULT_MIRROR_ROOT)
    parser.add_argument("--split-jsonl", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--protocol", default="p2")
    parser.add_argument(
        "--prompt-variants",
        nargs="+",
        default=["label_only", "evidence_guided", "conservative_off"],
        choices=sorted(PROMPTS),
    )
    parser.add_argument("--sample-limit", type=int, default=0, help="0 means full test set.")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--retry-backoff-seconds", type=float, default=2.0)
    return parser.parse_args()


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


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


def call_deepseek(api_key: str, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data


def call_deepseek_with_retry(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_retries: int,
    retry_backoff_seconds: float,
) -> dict[str, Any]:
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return call_deepseek(api_key, model, system_prompt, user_prompt)
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries:
                break
            time.sleep(retry_backoff_seconds * attempt)
    assert last_exc is not None
    raise last_exc


def parse_label(response_text: str) -> str:
    try:
        payload = json.loads(response_text)
        label = str(payload.get("label", "")).strip().lower()
        if label in {"yes", "no"}:
            return label
    except json.JSONDecodeError:
        pass
    lowered = response_text.lower()
    if '"label":"yes"' in lowered or '"label": "yes"' in lowered:
        return "yes"
    if '"label":"no"' in lowered or '"label": "no"' in lowered:
        return "no"
    raise ValueError(f"Could not parse label from response: {response_text[:200]}")


def binary_metrics(gold: list[int], pred: list[int]) -> dict[str, float | int]:
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
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "n": len(gold),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def main() -> None:
    args = parse_args()
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key in env var {args.api_key_env}")

    split_path = args.split_jsonl
    if split_path is None:
        split_path = args.mirror_root / "splits" / args.protocol / "test.jsonl"
    split_rows = load_jsonl(split_path)
    if args.sample_limit > 0:
        split_rows = split_rows[: args.sample_limit]

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []

    for variant in args.prompt_variants:
        spec = PROMPTS[variant]
        prediction_path = output_dir / f"{variant}_predictions.jsonl"
        existing_predictions = load_jsonl(prediction_path) if prediction_path.exists() else []
        completed_pair_ids = {row["pair_id"] for row in existing_predictions}
        predictions = list(existing_predictions)
        gold = []
        pred = []
        error_count = 0
        for row in existing_predictions:
            if row.get("had_error"):
                error_count += 1
                continue
            gold_label = int(row["gold_label"])
            pred_label = 1 if row["prediction_text"] == "yes" else 0
            gold.append(gold_label)
            pred.append(pred_label)
        total = len(split_rows)
        for idx, row in enumerate(split_rows, start=1):
            if row["split_pair_id"] in completed_pair_ids:
                if idx == 1 or idx % 25 == 0 or idx == total:
                    print(
                        f"[{variant}] {idx}/{total} checked; resumed={len(completed_pair_ids)} errors={error_count}",
                        file=sys.stderr,
                        flush=True,
                    )
                continue
            user_prompt = spec["user_template"].format(
                lang_a=row["ll1"],
                lang_b=row["ll2"],
                code_a=row["codeA"],
                code_b=row["codeB"],
            )
            try:
                response = call_deepseek_with_retry(
                    api_key=api_key,
                    model=args.model,
                    system_prompt=spec["system"],
                    user_prompt=user_prompt,
                    max_retries=args.max_retries,
                    retry_backoff_seconds=args.retry_backoff_seconds,
                )
                message = response["choices"][0]["message"]["content"]
                label_text = parse_label(message)
                usage = response.get("usage", {})
                had_error = False
            except Exception as exc:
                label_text = "error"
                usage = {}
                message = f"ERROR: {exc}"
                had_error = True
                error_count += 1
            pred_label = 1 if label_text == "yes" else 0
            gold_label = 1 if row["type"] == "clone" else 0
            if not had_error:
                gold.append(gold_label)
                pred.append(pred_label)
            pred_row = {
                "prompt_variant": variant,
                "pair_id": row["split_pair_id"],
                "lang_a": row["ll1"],
                "lang_b": row["ll2"],
                "problem_id_a": row["problem_id_1"],
                "problem_id_b": row["problem_id_2"],
                "gold_label_text": row["type"],
                "gold_label": gold_label,
                "prediction_text": label_text,
                "prediction_is_clone": label_text == "yes",
                "correct": (pred_label == gold_label) if not had_error else None,
                "had_error": had_error,
                "raw_response_text": message,
                "usage": usage,
            }
            predictions.append(pred_row)
            append_jsonl(prediction_path, pred_row)
            if (not had_error) and pred_label != gold_label:
                case_rows.append(pred_row)
            if idx == 1 or idx % 25 == 0 or idx == total:
                print(
                    f"[{variant}] {idx}/{total} done; errors={error_count}",
                    file=sys.stderr,
                    flush=True,
                )
            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

        metrics = binary_metrics(gold, pred)
        print(
            f"[{variant}] completed; effective_n={len(gold)} errors={error_count} "
            f"precision={metrics['precision']:.4f} recall={metrics['recall']:.4f} f1={metrics['f1']:.4f}",
            file=sys.stderr,
            flush=True,
        )
        summary_rows.append(
            {
                "protocol": args.protocol,
                "model": args.model,
                "prompt_variant": variant,
                "resumed_rows": len(existing_predictions),
                "error_count": error_count,
                "effective_n": len(gold),
                **metrics,
            }
        )

    write_csv(output_dir / "deepseek_prompt_ablation_p2.csv", summary_rows)
    write_jsonl(output_dir / "deepseek_prompt_ablation_cases.jsonl", case_rows)
    write_json(
        output_dir / "deepseek_prompt_ablation_manifest.json",
        {
            "protocol": args.protocol,
            "model": args.model,
            "prompt_variants": args.prompt_variants,
            "sample_limit": args.sample_limit,
            "output_dir": str(output_dir),
        },
    )

    print(json.dumps({"output_dir": str(output_dir), "rows": len(summary_rows)}, indent=2))


if __name__ == "__main__":
    main()
