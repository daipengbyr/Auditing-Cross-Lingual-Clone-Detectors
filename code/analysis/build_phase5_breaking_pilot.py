#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from build_phase5_preserving_pilot import (
    TARGET_LANGS,
    DEFAULT_NODE,
    write_csv,
    write_json,
    write_jsonl,
    validate_for_language,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PILOT = ROOT / "outputs" / "third_round_phase5_preserving_pilot_20260627" / "semantic_preserving_pilot.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "third_round_phase5_breaking_pilot_20260628"


@dataclass
class BreakResult:
    ok: bool
    transformed_code: str | None
    transformation_type: str | None
    validation_status: str
    validator: str
    validation_detail: str
    candidate_count: int
    skip_reason: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 5B semantic-breaking pilot from Phase 5A source pairs.")
    parser.add_argument("--source-pilot-jsonl", type=Path, default=DEFAULT_SOURCE_PILOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--node-bin", type=Path, default=DEFAULT_NODE)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def rewrite_first(pattern: str, repl: str | Callable[[re.Match[str]], str], code: str) -> tuple[str, int]:
    return re.subn(pattern, repl, code, count=1, flags=re.MULTILINE)


def flip_yes_no_string(code: str) -> tuple[str, int]:
    patterns = [
        (r'"Yes"', '"No"'),
        (r'"No"', '"Yes"'),
        (r'"YES"', '"NO"'),
        (r'"NO"', '"YES"'),
        (r'"yes"', '"no"'),
        (r'"no"', '"yes"'),
        (r"'Yes'", "'No'"),
        (r"'No'", "'Yes'"),
        (r"'YES'", "'NO'"),
        (r"'NO'", "'YES'"),
        (r"'yes'", "'no'"),
        (r"'no'", "'yes'"),
    ]
    for pattern, repl in patterns:
        new_code, n = rewrite_first(pattern, repl, code)
        if n:
            return new_code, n
    return code, 0


def flip_boolean_literal(lang: str, code: str) -> tuple[str, int]:
    if lang == "Python":
        patterns = [(r"\bTrue\b", "False"), (r"\bFalse\b", "True")]
    else:
        patterns = [(r"\btrue\b", "false"), (r"\bfalse\b", "true")]
    for pattern, repl in patterns:
        new_code, n = rewrite_first(pattern, repl, code)
        if n:
            return new_code, n
    return code, 0


def flip_comparator(lang: str, code: str) -> tuple[str, int]:
    patterns: list[tuple[str, str]] = []
    if lang == "JavaScript":
        patterns.extend([
            (r"!==", "==="),
            (r"===", "!=="),
        ])
    patterns.extend([
        (r"<=", "<"),
        (r">=", ">"),
        (r"(?<![=!<>])==(?![=])", "!="),
        (r"!=", "=="),
        (r"(?<![<])<(?![=])", "<="),
        (r"(?<![>])>(?![=])", ">="),
    ])
    for pattern, repl in patterns:
        new_code, n = rewrite_first(pattern, repl, code)
        if n:
            return new_code, n
    return code, 0


def flip_update_operator(code: str) -> tuple[str, int]:
    patterns = [
        (r"\+\+", "--"),
        (r"--", "++"),
        (r"\+=", "-="),
        (r"-=", "+="),
        (r"\*=", "/="),
        (r"/=", "*="),
    ]
    for pattern, repl in patterns:
        new_code, n = rewrite_first(pattern, repl, code)
        if n:
            return new_code, n
    return code, 0


def perturb_integer_literal(code: str) -> tuple[str, int]:
    def repl(match: re.Match[str]) -> str:
        text = match.group(0)
        try:
            value = int(text)
        except ValueError:
            return text
        if value == 0:
            return "1"
        if value > 0:
            return str(value + 1)
        return str(value - 1)

    return rewrite_first(r"(?<![A-Za-z_])(?:0|[1-9]\d*)(?![A-Za-z_])", repl, code)


TRANSFORMS: list[tuple[str, Callable[[str, str], tuple[str, int]]]] = [
    ("answer_string_flip", lambda lang, code: flip_yes_no_string(code)),
    ("boolean_literal_flip", flip_boolean_literal),
    ("comparator_flip", flip_comparator),
    ("update_operator_flip", lambda lang, code: flip_update_operator(code)),
    ("integer_literal_perturb", lambda lang, code: perturb_integer_literal(code)),
]


def transform_semantic_break(lang: str, code: str, node_bin: Path) -> BreakResult:
    candidate_count = 0
    for transformation_type, fn in TRANSFORMS:
        transformed, n = fn(lang, code)
        candidate_count += 1
        if not n or transformed == code:
            continue
        status, validator, detail = validate_for_language(lang, transformed, node_bin)
        if status == "auto_fail":
            continue
        return BreakResult(
            ok=True,
            transformed_code=transformed,
            transformation_type=transformation_type,
            validation_status=status,
            validator=validator,
            validation_detail=detail,
            candidate_count=candidate_count,
        )
    return BreakResult(
        ok=False,
        transformed_code=None,
        transformation_type=None,
        validation_status="skip",
        validator="none",
        validation_detail="",
        candidate_count=candidate_count,
        skip_reason="no_breaking_transform_succeeded",
    )


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    rows = load_jsonl(args.source_pilot_jsonl.resolve())
    rows = [row for row in rows if row["lang_b"] in TARGET_LANGS]
    rng.shuffle(rows)

    built_rows: list[dict[str, Any]] = []
    model_input_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    manual_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []

    counts_by_lang: dict[str, dict[str, int]] = {lang: {"selected_rows": 0, "auto_pass": 0, "manual_required": 0, "skip": 0} for lang in TARGET_LANGS}

    for row in rows:
        lang = row["lang_b"]
        result = transform_semantic_break(
            lang=lang,
            code=row["original_codeB"],
            node_bin=args.node_bin,
        )
        counts_by_lang[lang][result.validation_status] = counts_by_lang[lang].get(result.validation_status, 0) + 1
        record = {
            "phase": "phase5b",
            "protocol": "p2",
            "variant_kind": "semantic_breaking",
            "transformation_type": result.transformation_type,
            "transform_target": "codeB",
            "source_pair_id": row["source_pair_id"],
            "problem_id": row["problem_id"],
            "lang_a": row["lang_a"],
            "lang_b": lang,
            "label": "nonclone",
            "validation_status": result.validation_status,
            "validator": result.validator,
            "validation_detail": result.validation_detail,
            "candidate_count": result.candidate_count,
            "skip_reason": result.skip_reason,
            "original_codeA": row["original_codeA"],
            "original_codeB": row["original_codeB"],
            "transformed_codeB": result.transformed_code,
            "rename_map": row.get("rename_map", {}),
            "normalized_code_hash_a": row.get("normalized_code_hash_a"),
            "normalized_code_hash_b": row.get("normalized_code_hash_b"),
            "exact_pair_hash": row.get("exact_pair_hash"),
        }
        if result.ok:
            counts_by_lang[lang]["selected_rows"] += 1
            built_rows.append(record)
            model_input_rows.append(
                {
                    "split_pair_id": f"{row['source_pair_id']}__break_{result.transformation_type}",
                    "source_pair_id": row["source_pair_id"],
                    "problem_id_1": row["problem_id"],
                    "problem_id_2": row["problem_id"],
                    "ll1": row["lang_a"],
                    "ll2": lang,
                    "type": "nonclone",
                    "codeA": row["original_codeA"],
                    "codeB": result.transformed_code,
                    "semantic_variant_kind": "semantic_breaking",
                    "transformation_type": result.transformation_type,
                    "transform_target": "codeB",
                    "validation_status": result.validation_status,
                    "validator": result.validator,
                    "normalized_code_hash_a": row.get("normalized_code_hash_a"),
                    "normalized_code_hash_b": row.get("normalized_code_hash_b"),
                    "exact_pair_hash": row.get("exact_pair_hash"),
                }
            )
            summary_rows.append(
                {
                    "source_pair_id": row["source_pair_id"],
                    "lang_b": lang,
                    "problem_id": row["problem_id"],
                    "transformation_type": result.transformation_type,
                    "validation_status": result.validation_status,
                    "validator": result.validator,
                    "skip_reason": result.skip_reason or "",
                }
            )
            if result.validation_status != "auto_pass":
                manual_rows.append(
                    {
                        "source_pair_id": row["source_pair_id"],
                        "lang_b": lang,
                        "transformation_type": result.transformation_type,
                        "validator": result.validator,
                        "validation_detail": result.validation_detail,
                    }
                )
        else:
            rejected_rows.append(
                {
                    "source_pair_id": row["source_pair_id"],
                    "lang_b": lang,
                    "candidate_count": result.candidate_count,
                    "skip_reason": result.skip_reason,
                }
            )

    lang_summary = []
    for lang in TARGET_LANGS:
        lang_summary.append(
            {
                "lang_b": lang,
                **counts_by_lang[lang],
            }
        )

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "semantic_breaking_pilot.jsonl", built_rows)
    write_jsonl(output_dir / "semantic_breaking_model_input.jsonl", model_input_rows)
    write_csv(output_dir / "semantic_breaking_summary.csv", summary_rows)
    write_csv(output_dir / "semantic_breaking_manual_audit.csv", manual_rows)
    write_csv(output_dir / "semantic_breaking_rejected_attempts.csv", rejected_rows)
    write_csv(output_dir / "semantic_breaking_lang_summary.csv", lang_summary)
    write_json(
        output_dir / "semantic_breaking_manifest.json",
        {
            "phase": "phase5b",
            "description": "Semantic-breaking pilot built from the same source pairs as the Phase 5A preserving pilot.",
            "seed": args.seed,
            "input_source_pilot_jsonl": str(args.source_pilot_jsonl.resolve()),
            "node_bin": str(args.node_bin),
            "selected_rows_total": len(model_input_rows),
            "lang_summary": lang_summary,
            "transform_types": [name for name, _ in TRANSFORMS],
            "output_files": {
                "pilot_jsonl": str((output_dir / "semantic_breaking_pilot.jsonl").resolve()),
                "model_input_jsonl": str((output_dir / "semantic_breaking_model_input.jsonl").resolve()),
                "summary_csv": str((output_dir / "semantic_breaking_summary.csv").resolve()),
                "manual_audit_csv": str((output_dir / "semantic_breaking_manual_audit.csv").resolve()),
                "rejected_attempts_csv": str((output_dir / "semantic_breaking_rejected_attempts.csv").resolve()),
            },
        },
    )
    print(json.dumps({"output_dir": str(output_dir), "selected_rows_total": len(model_input_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
