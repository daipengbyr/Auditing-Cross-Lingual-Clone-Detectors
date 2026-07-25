#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from build_phase5_preserving_pilot import TARGET_LANGS, DEFAULT_NODE, validate_for_language, write_csv, write_json, write_jsonl


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PILOT = ROOT / "outputs" / "third_round_phase5_preserving_pilot_20260627" / "semantic_preserving_pilot.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "third_round_phase5_breaking_v2_mini_20260628"


@dataclass
class BreakResult:
    ok: bool
    transformed_code: str | None
    transformation_type: str | None
    validation_status: str
    validator: str
    validation_detail: str
    skip_reason: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a stronger Phase 5 breaking_v2 mini pilot.")
    parser.add_argument("--source-pilot-jsonl", type=Path, default=DEFAULT_SOURCE_PILOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--per-language", type=int, default=8)
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


def replace_last_match(pattern: str, code: str, repl_fn) -> tuple[str, int]:
    matches = list(re.finditer(pattern, code, flags=re.MULTILINE))
    if not matches:
        return code, 0
    match = matches[-1]
    repl = repl_fn(match)
    new_code = code[: match.start()] + repl + code[match.end() :]
    return new_code, 1


def output_string_flip(code: str) -> tuple[str, str | None]:
    pairs = [
        ('"Yes"', '"No"'),
        ('"No"', '"Yes"'),
        ('"YES"', '"NO"'),
        ('"NO"', '"YES"'),
        ('"safe"', '"unsafe"'),
        ('"unsafe"', '"safe"'),
        ('"Alice"', '"Bob"'),
        ('"Bob"', '"Alice"'),
        ("'Yes'", "'No'"),
        ("'No'", "'Yes'"),
        ("'safe'", "'unsafe'"),
        ("'unsafe'", "'safe'"),
    ]
    for old, new in pairs:
        if old in code:
            idx = code.rfind(old)
            return code[:idx] + new + code[idx + len(old) :], "output_string_flip"
    return code, None


def python_break(code: str) -> tuple[str, str | None]:
    new_code, name = output_string_flip(code)
    if name:
        return new_code, name
    pattern = r"print\(([^()\n][^\n]*)\)"
    def repl(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr.startswith(("'", '"')):
            return m.group(0)
        return f"print(({expr}) + 1)"
    new_code, n = replace_last_match(pattern, code, repl)
    if n and new_code != code:
        return new_code, "final_print_expr_perturb"
    pattern = r"return\s+([^\n#]+)"
    def repl_ret(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr in {"True", "False", "None"} or expr.startswith(("'", '"')):
            return f"return {expr}"
        return f"return ({expr}) + 1"
    new_code, n = replace_last_match(pattern, code, repl_ret)
    if n and new_code != code:
        return new_code, "final_return_expr_perturb"
    return code, None


def js_break(code: str) -> tuple[str, str | None]:
    new_code, name = output_string_flip(code)
    if name:
        return new_code, name
    pattern = r"console\.log\(([^)\n]+)\);?"
    def repl(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr.startswith(("'", '"')):
            return m.group(0)
        return f"console.log(({expr}) + 1);"
    new_code, n = replace_last_match(pattern, code, repl)
    if n and new_code != code:
        return new_code, "final_console_expr_perturb"
    pattern = r"return\s+([^;\n]+)"
    def repl_ret(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr in {"true", "false", "null"} or expr.startswith(("'", '"')):
            return f"return {expr}"
        return f"return ({expr}) + 1"
    new_code, n = replace_last_match(pattern, code, repl_ret)
    if n and new_code != code:
        return new_code, "final_return_expr_perturb"
    return code, None


def go_break(code: str) -> tuple[str, str | None]:
    new_code, name = output_string_flip(code)
    if name:
        return new_code, name
    pattern = r"fmt\.Print(?:ln)?\(([^)\n]+)\)"
    def repl(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if "," in expr:
            return m.group(0)
        if expr.startswith(("`", '"')):
            return m.group(0)
        fn = "Println" if "Println" in m.group(0) else "Print"
        return f"fmt.{fn}(({expr}) + 1)"
    new_code, n = replace_last_match(pattern, code, repl)
    if n and new_code != code:
        return new_code, "final_print_expr_perturb"
    pattern = r"return\s+([^\n/]+)"
    def repl_ret(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if "," in expr or expr.startswith(("`", '"')):
            return m.group(0)
        return f"return ({expr}) + 1"
    new_code, n = replace_last_match(pattern, code, repl_ret)
    if n and new_code != code:
        return new_code, "final_return_expr_perturb"
    return code, None


def cpp_break(code: str) -> tuple[str, str | None]:
    new_code, name = output_string_flip(code)
    if name:
        return new_code, name
    pattern = r"cout\s*<<\s*([^<\n;]+)\s*<<\s*endl"
    def repl_cout_endl(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr in {"endl", "std::endl"} or expr.startswith(("'", '"')):
            return m.group(0)
        return f"cout << (({expr}) + 1) << endl"
    new_code, n = replace_last_match(pattern, code, repl_cout_endl)
    if n and new_code != code:
        return new_code, "final_cout_expr_perturb"
    pattern = r"printf\((\"[^\"]*\"),\s*([^)]+)\)"
    def repl_printf(m: re.Match[str]) -> str:
        fmt = m.group(1)
        expr = m.group(2).strip()
        return f'printf({fmt}, ({expr}) + 1)'
    new_code, n = replace_last_match(pattern, code, repl_printf)
    if n and new_code != code:
        return new_code, "final_printf_expr_perturb"
    pattern = r"cout\s*<<\s*([^;<\n]+)"
    def repl_cout(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr in {"endl", "std::endl"} or expr.startswith(("'", '"')):
            return m.group(0)
        return f"cout << (({expr}) + 1)"
    new_code, n = replace_last_match(pattern, code, repl_cout)
    if n and new_code != code:
        return new_code, "final_cout_expr_perturb"
    pattern = r"return\s+([^;\n]+);"
    def repl_ret(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr.startswith(("'", '"')):
            return m.group(0)
        return f"return ({expr}) + 1;"
    new_code, n = replace_last_match(pattern, code, repl_ret)
    if n and new_code != code:
        return new_code, "final_return_expr_perturb"
    return code, None


def transform_semantic_break_v2(lang: str, code: str, node_bin: Path) -> BreakResult:
    if lang == "Python":
        transformed, transformation_type = python_break(code)
    elif lang == "JavaScript":
        transformed, transformation_type = js_break(code)
    elif lang == "Go":
        transformed, transformation_type = go_break(code)
    elif lang == "C++":
        transformed, transformation_type = cpp_break(code)
    else:
        transformed, transformation_type = code, None
    if not transformation_type or transformed == code:
        return BreakResult(False, None, None, "skip", "none", "", "no_v2_transform_hit")
    status, validator, detail = validate_for_language(lang, transformed, node_bin)
    if status == "auto_fail":
        return BreakResult(False, None, transformation_type, status, validator, detail, "validation_failed")
    return BreakResult(True, transformed, transformation_type, status, validator, detail)


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    rows = load_jsonl(args.source_pilot_jsonl.resolve())
    by_lang: dict[str, list[dict[str, Any]]] = {lang: [] for lang in TARGET_LANGS}
    for row in rows:
        if row["lang_b"] in TARGET_LANGS:
            by_lang[row["lang_b"]].append(row)
    for lang_rows in by_lang.values():
        rng.shuffle(lang_rows)

    built_rows: list[dict[str, Any]] = []
    model_input_rows: list[dict[str, Any]] = []
    manual_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    lang_summary: list[dict[str, Any]] = []

    for lang in TARGET_LANGS:
        selected = 0
        attempts = 0
        auto_pass = 0
        manual_required = 0
        skip = 0
        for row in by_lang[lang]:
            if selected >= args.per_language:
                break
            attempts += 1
            result = transform_semantic_break_v2(lang, row["original_codeB"], args.node_bin)
            if not result.ok:
                skip += 1
                rejected_rows.append(
                    {
                        "source_pair_id": row["source_pair_id"],
                        "lang_b": lang,
                        "skip_reason": result.skip_reason,
                        "validation_detail": result.validation_detail,
                    }
                )
                continue
            selected += 1
            if result.validation_status == "auto_pass":
                auto_pass += 1
            else:
                manual_required += 1
                manual_rows.append(
                    {
                        "source_pair_id": row["source_pair_id"],
                        "lang_b": lang,
                        "transformation_type": result.transformation_type,
                        "validator": result.validator,
                        "validation_detail": result.validation_detail,
                    }
                )
            built_rows.append(
                {
                    "phase": "phase5b_v2",
                    "protocol": "p2",
                    "variant_kind": "semantic_breaking_v2",
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
                    "original_codeA": row["original_codeA"],
                    "original_codeB": row["original_codeB"],
                    "transformed_codeB": result.transformed_code,
                    "normalized_code_hash_a": row.get("normalized_code_hash_a"),
                    "normalized_code_hash_b": row.get("normalized_code_hash_b"),
                    "exact_pair_hash": row.get("exact_pair_hash"),
                }
            )
            model_input_rows.append(
                {
                    "split_pair_id": f"{row['source_pair_id']}__breakv2_{result.transformation_type}",
                    "source_pair_id": row["source_pair_id"],
                    "problem_id_1": row["problem_id"],
                    "problem_id_2": row["problem_id"],
                    "ll1": row["lang_a"],
                    "ll2": lang,
                    "type": "nonclone",
                    "codeA": row["original_codeA"],
                    "codeB": result.transformed_code,
                    "semantic_variant_kind": "semantic_breaking_v2",
                    "transformation_type": result.transformation_type,
                    "transform_target": "codeB",
                    "validation_status": result.validation_status,
                    "validator": result.validator,
                    "normalized_code_hash_a": row.get("normalized_code_hash_a"),
                    "normalized_code_hash_b": row.get("normalized_code_hash_b"),
                    "exact_pair_hash": row.get("exact_pair_hash"),
                }
            )
        lang_summary.append(
            {
                "lang_b": lang,
                "attempted_rows": attempts,
                "selected_rows": selected,
                "auto_pass": auto_pass,
                "manual_required": manual_required,
                "skip": skip,
            }
        )

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "semantic_breaking_v2_pilot.jsonl", built_rows)
    write_jsonl(output_dir / "semantic_breaking_v2_model_input.jsonl", model_input_rows)
    write_csv(output_dir / "semantic_breaking_v2_manual_audit.csv", manual_rows)
    write_csv(output_dir / "semantic_breaking_v2_rejected_attempts.csv", rejected_rows)
    write_csv(output_dir / "semantic_breaking_v2_lang_summary.csv", lang_summary)
    write_json(
        output_dir / "semantic_breaking_v2_manifest.json",
        {
            "phase": "phase5b_v2",
            "description": "Stronger semantic-breaking v2 mini pilot targeting final output or final return expressions.",
            "seed": args.seed,
            "per_language": args.per_language,
            "selected_rows_total": len(model_input_rows),
            "input_source_pilot_jsonl": str(args.source_pilot_jsonl.resolve()),
            "lang_summary": lang_summary,
            "output_files": {
                "pilot_jsonl": str((output_dir / "semantic_breaking_v2_pilot.jsonl").resolve()),
                "model_input_jsonl": str((output_dir / "semantic_breaking_v2_model_input.jsonl").resolve()),
            },
        },
    )
    print(json.dumps({"output_dir": str(output_dir), "selected_rows_total": len(model_input_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
