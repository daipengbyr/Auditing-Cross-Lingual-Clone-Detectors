#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import builtins
import json
import keyword
import random
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPLIT_JSONL = (
    ROOT
    / "outputs"
    / "third_round_remote_mirror_20260626"
    / "splits"
    / "p2"
    / "test.jsonl"
)
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "third_round_phase5_preserving_pilot_20260627"
DEFAULT_NODE = Path(
    "/Users/daipeng/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
)

TARGET_LANGS = ["Python", "C++", "Go", "JavaScript"]

CPP_DECL_RE = re.compile(
    r"\b(?:int|long|long\s+int|long\s+long|ll|bool|double|float|char|string|auto|size_t|llong|ld)\s+([A-Za-z_]\w*)\b"
)
CPP_FOR_RE = re.compile(
    r"for\s*\(\s*(?:int|long|long\s+long|ll|size_t|auto)\s+([A-Za-z_]\w*)\b"
)
JS_DECL_RE = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\b")
JS_FUNC_RE = re.compile(r"function\s+[A-Za-z_$][A-Za-z0-9_$]*\s*\(([^)]*)\)")
GO_SHORT_RE = re.compile(r"\b([A-Za-z_]\w*)\s*:=")
GO_VAR_RE = re.compile(r"\bvar\s+([A-Za-z_]\w*)\b")
GO_FUNC_RE = re.compile(r"func\s+[A-Za-z_]\w*\s*\(([^)]*)\)")

COMMON_RESERVED = {
    "main",
    "solve",
    "ans",
    "stdin",
    "stdout",
    "scanf",
    "printf",
    "println",
    "print",
    "input",
    "range",
    "len",
    "append",
    "make",
    "new",
    "true",
    "false",
    "null",
    "nil",
}


@dataclass
class TransformResult:
    ok: bool
    transformed_code: str | None
    rename_map: dict[str, str]
    candidate_count: int
    applied_count: int
    validation_status: str
    validator: str
    validation_detail: str
    skip_reason: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 5A semantic-preserving pilot.")
    parser.add_argument("--split-jsonl", type=Path, default=DEFAULT_SPLIT_JSONL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=20260627)
    parser.add_argument("--per-language", type=int, default=25)
    parser.add_argument("--max-renames", type=int, default=3)
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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    import csv

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


def python_candidates(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    imported: set[str] = set()
    assigned: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import) -> Any:
            for alias in node.names:
                imported.add(alias.asname or alias.name.split(".")[0])

        def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
            for alias in node.names:
                imported.add(alias.asname or alias.name)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            imported.add(node.name)
            for arg in node.args.args + node.args.kwonlyargs:
                assigned.append(arg.arg)
            if node.args.vararg:
                assigned.append(node.args.vararg.arg)
            if node.args.kwarg:
                assigned.append(node.args.kwarg.arg)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> Any:
            imported.add(node.name)
            self.generic_visit(node)

        def visit_Name(self, node: ast.Name) -> Any:
            if isinstance(node.ctx, ast.Store):
                assigned.append(node.id)

    Visitor().visit(tree)
    builtins_set = set(dir(builtins))
    out = []
    seen = set()
    for name in assigned:
        if name in seen:
            continue
        seen.add(name)
        if (
            name in imported
            or name in builtins_set
            or keyword.iskeyword(name)
            or name.startswith("__")
            or len(name) <= 1
            or name in COMMON_RESERVED
        ):
            continue
        out.append(name)
    return out


def extract_params(param_blob: str) -> list[str]:
    out: list[str] = []
    for piece in param_blob.split(","):
        piece = piece.strip()
        if not piece:
            continue
        piece = re.sub(r"=.*$", "", piece).strip()
        piece = re.sub(r"^\.\.\.", "", piece).strip()
        piece = piece.split(":")[0].strip()
        parts = piece.split()
        if parts:
            name = parts[-1]
            if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name):
                out.append(name)
    return out


def js_candidates(code: str) -> list[str]:
    names = JS_DECL_RE.findall(code)
    for blob in JS_FUNC_RE.findall(code):
        names.extend(extract_params(blob))
    out = []
    seen = set()
    reserved = {
        "require", "console", "process", "Math", "Number", "BigInt", "String", "Array",
        "Object", "Set", "Map", "main", "Main", *COMMON_RESERVED,
    }
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        if name in reserved or len(name) <= 1:
            continue
        out.append(name)
    return out


def go_candidates(code: str) -> list[str]:
    names = GO_SHORT_RE.findall(code) + GO_VAR_RE.findall(code)
    for blob in GO_FUNC_RE.findall(code):
        names.extend(extract_params(blob))
    out = []
    seen = set()
    reserved = {"fmt", "os", "bufio", "strconv", "main", "len", "make", "append", "string", "int", *COMMON_RESERVED}
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        if name in reserved or len(name) <= 1 or name[0].isupper():
            continue
        out.append(name)
    return out


def cpp_candidates(code: str) -> list[str]:
    names = CPP_DECL_RE.findall(code) + CPP_FOR_RE.findall(code)
    out = []
    seen = set()
    reserved = {
        "main", "cout", "cin", "endl", "std", "vector", "string", "pair", "auto",
        "int", "long", "ll", "llong", "ld", "char", "bool", *COMMON_RESERVED,
    }
    for name in names:
        name = name.strip()
        if name in seen:
            continue
        seen.add(name)
        if name in reserved:
            continue
        out.append(name)
    return out


def make_new_name(lang: str, index: int, existing: set[str]) -> str:
    base = "renamed_var" if lang == "Python" else "renamedVar"
    candidate = f"{base}_{index}" if lang == "Python" else f"{base}{index}"
    while candidate in existing:
        index += 1
        candidate = f"{base}_{index}" if lang == "Python" else f"{base}{index}"
    return candidate


def apply_renames(code: str, rename_map: dict[str, str]) -> str:
    renamed = code
    for old in sorted(rename_map, key=len, reverse=True):
        new = rename_map[old]
        renamed = re.sub(rf"\b{re.escape(old)}\b", new, renamed)
    return renamed


def validate_python(code: str) -> tuple[str, str, str]:
    try:
        ast.parse(code)
        return "auto_pass", "python_ast", "ok"
    except SyntaxError as exc:
        return "auto_fail", "python_ast", f"{exc.__class__.__name__}: {exc}"


def validate_cpp(code: str) -> tuple[str, str, str]:
    try:
        proc = subprocess.run(
            ["/usr/bin/g++", "-std=c++17", "-fsyntax-only", "-x", "c++", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return "manual_required", "g++", f"validator_unavailable: {exc}"
    joined = (proc.stderr or proc.stdout).strip()
    if "bits/stdc++.h" in joined and "file not found" in joined:
        return "manual_required", "g++_header_limited", "bits_header_not_available_in_local_validator"
    if proc.returncode == 0:
        return "auto_pass", "g++", "ok"
    detail = joined.splitlines()[:3]
    return "auto_fail", "g++", " | ".join(detail) if detail else "syntax_error"


def validate_javascript(code: str, node_bin: Path) -> tuple[str, str, str]:
    if not node_bin.exists():
        return "manual_required", "node_check", "node_runtime_missing"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as handle:
        tmp = Path(handle.name)
        handle.write(code)
    try:
        proc = subprocess.run(
            [str(node_bin), "--check", str(tmp)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0:
            return "auto_pass", "node_check", "ok"
        detail = (proc.stderr or proc.stdout).strip().splitlines()[:3]
        return "auto_fail", "node_check", " | ".join(detail) if detail else "syntax_error"
    finally:
        tmp.unlink(missing_ok=True)


def validate_go(code: str) -> tuple[str, str, str]:
    open_braces = code.count("{")
    close_braces = code.count("}")
    open_parens = code.count("(")
    close_parens = code.count(")")
    if open_braces == close_braces and open_parens == close_parens:
        return "manual_required", "brace_balance_only", "balanced_tokens_no_go_parser"
    return "auto_fail", "brace_balance_only", "unbalanced_tokens"


def rename_candidates_for_language(lang: str, code: str) -> list[str]:
    if lang == "Python":
        return python_candidates(code)
    if lang == "JavaScript":
        return js_candidates(code)
    if lang == "Go":
        return go_candidates(code)
    if lang == "C++":
        return cpp_candidates(code)
    return []


def validate_for_language(lang: str, code: str, node_bin: Path) -> tuple[str, str, str]:
    if lang == "Python":
        return validate_python(code)
    if lang == "JavaScript":
        return validate_javascript(code, node_bin)
    if lang == "C++":
        return validate_cpp(code)
    if lang == "Go":
        return validate_go(code)
    return "manual_required", "none", "no_validator"


def transform_identifier_rename(
    lang: str,
    code: str,
    max_renames: int,
    node_bin: Path,
) -> TransformResult:
    candidates = rename_candidates_for_language(lang, code)
    if not candidates:
        return TransformResult(
            ok=False,
            transformed_code=None,
            rename_map={},
            candidate_count=0,
            applied_count=0,
            validation_status="skip",
            validator="none",
            validation_detail="",
            skip_reason="no_safe_candidates",
        )
    existing = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", code))
    rename_map: dict[str, str] = {}
    for idx, old in enumerate(candidates[:max_renames], start=1):
        rename_map[old] = make_new_name(lang, idx, existing | set(rename_map.values()))
    transformed = apply_renames(code, rename_map)
    if transformed == code:
        return TransformResult(
            ok=False,
            transformed_code=None,
            rename_map=rename_map,
            candidate_count=len(candidates),
            applied_count=0,
            validation_status="skip",
            validator="none",
            validation_detail="",
            skip_reason="rewrite_no_effect",
        )
    status, validator, detail = validate_for_language(lang, transformed, node_bin)
    return TransformResult(
        ok=status != "auto_fail",
        transformed_code=transformed if status != "auto_fail" else None,
        rename_map=rename_map,
        candidate_count=len(candidates),
        applied_count=len(rename_map),
        validation_status=status,
        validator=validator,
        validation_detail=detail,
        skip_reason=None if status != "auto_fail" else "validation_failed",
    )


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    rows = load_jsonl(args.split_jsonl.resolve())
    positives = [row for row in rows if row["type"] == "clone" and row["ll2"] in TARGET_LANGS]

    by_lang: dict[str, list[dict[str, Any]]] = {lang: [] for lang in TARGET_LANGS}
    for row in positives:
        by_lang[row["ll2"]].append(row)
    for lang_rows in by_lang.values():
        rng.shuffle(lang_rows)

    built_rows: list[dict[str, Any]] = []
    model_input_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    manual_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []

    lang_summary = []
    total_selected = 0
    for lang in TARGET_LANGS:
        accepted = 0
        attempts = 0
        counts = {"auto_pass": 0, "manual_required": 0, "auto_fail": 0, "skip": 0}
        for row in by_lang[lang]:
            if accepted >= args.per_language:
                break
            attempts += 1
            result = transform_identifier_rename(
                lang=lang,
                code=row["codeB"],
                max_renames=args.max_renames,
                node_bin=args.node_bin,
            )
            counts[result.validation_status] = counts.get(result.validation_status, 0) + 1
            record = {
                "phase": "phase5a",
                "protocol": "p2",
                "variant_kind": "semantic_preserving",
                "transformation_type": "identifier_rename",
                "transform_target": "codeB",
                "source_pair_id": row["split_pair_id"],
                "problem_id": row["problem_id_1"],
                "lang_a": row["ll1"],
                "lang_b": lang,
                "label": row["type"],
                "validation_status": result.validation_status,
                "validator": result.validator,
                "validation_detail": result.validation_detail,
                "candidate_identifier_count": result.candidate_count,
                "applied_rename_count": result.applied_count,
                "rename_map": result.rename_map,
                "skip_reason": result.skip_reason,
                "original_codeA": row["codeA"],
                "original_codeB": row["codeB"],
                "transformed_codeB": result.transformed_code,
                "normalized_code_hash_a": row.get("normalized_code_hash_a"),
                "normalized_code_hash_b": row.get("normalized_code_hash_b"),
                "exact_pair_hash": row.get("exact_pair_hash"),
            }
            if result.ok:
                accepted += 1
                total_selected += 1
                built_rows.append(record)
                model_input_rows.append(
                    {
                        "split_pair_id": f"{row['split_pair_id']}__preserve_idrename",
                        "source_pair_id": row["split_pair_id"],
                        "problem_id_1": row["problem_id_1"],
                        "problem_id_2": row["problem_id_2"],
                        "ll1": row["ll1"],
                        "ll2": lang,
                        "type": "clone",
                        "codeA": row["codeA"],
                        "codeB": result.transformed_code,
                        "semantic_variant_kind": "semantic_preserving",
                        "transformation_type": "identifier_rename",
                        "transform_target": "codeB",
                        "validation_status": result.validation_status,
                        "validator": result.validator,
                        "rename_map": result.rename_map,
                        "normalized_code_hash_a": row.get("normalized_code_hash_a"),
                        "normalized_code_hash_b": row.get("normalized_code_hash_b"),
                        "exact_pair_hash": row.get("exact_pair_hash"),
                    }
                )
                summary_rows.append(
                    {
                        "source_pair_id": row["split_pair_id"],
                        "lang_b": lang,
                        "problem_id": row["problem_id_1"],
                        "validation_status": result.validation_status,
                        "validator": result.validator,
                        "candidate_identifier_count": result.candidate_count,
                        "applied_rename_count": result.applied_count,
                        "skip_reason": result.skip_reason or "",
                    }
                )
                if result.validation_status != "auto_pass":
                    manual_rows.append(
                        {
                            "source_pair_id": row["split_pair_id"],
                            "lang_b": lang,
                            "problem_id": row["problem_id_1"],
                            "validation_status": result.validation_status,
                            "validator": result.validator,
                            "validation_detail": result.validation_detail,
                            "skip_reason": result.skip_reason or "",
                            "rename_map": json.dumps(result.rename_map, ensure_ascii=False),
                        }
                    )
            else:
                rejected_rows.append(
                    {
                        "source_pair_id": row["split_pair_id"],
                        "lang_b": lang,
                        "problem_id": row["problem_id_1"],
                        "validation_status": result.validation_status,
                        "validator": result.validator,
                        "validation_detail": result.validation_detail,
                        "skip_reason": result.skip_reason or "",
                        "rename_map": json.dumps(result.rename_map, ensure_ascii=False),
                    }
                )
        lang_summary.append(
            {
                "lang_b": lang,
                "attempted_rows": attempts,
                "selected_rows": accepted,
                **counts,
            }
        )

    manifest = {
        "phase": "phase5a",
        "description": "Semantic-preserving pilot builder using identifier renaming on P2 positive pairs.",
        "seed": args.seed,
        "per_language": args.per_language,
        "max_renames": args.max_renames,
        "target_languages": TARGET_LANGS,
        "input_split_jsonl": str(args.split_jsonl.resolve()),
        "node_bin": str(args.node_bin),
        "selected_rows_total": total_selected,
        "lang_summary": lang_summary,
        "output_files": {
            "pilot_jsonl": str((args.output_dir / "semantic_preserving_pilot.jsonl").resolve()),
            "model_input_jsonl": str((args.output_dir / "semantic_preserving_model_input.jsonl").resolve()),
            "summary_csv": str((args.output_dir / "semantic_preserving_summary.csv").resolve()),
            "manual_audit_csv": str((args.output_dir / "semantic_preserving_manual_audit.csv").resolve()),
            "rejected_attempts_csv": str((args.output_dir / "semantic_preserving_rejected_attempts.csv").resolve()),
        },
    }

    write_jsonl(args.output_dir / "semantic_preserving_pilot.jsonl", built_rows)
    write_jsonl(args.output_dir / "semantic_preserving_model_input.jsonl", model_input_rows)
    write_csv(args.output_dir / "semantic_preserving_summary.csv", summary_rows)
    write_csv(args.output_dir / "semantic_preserving_manual_audit.csv", manual_rows)
    write_csv(args.output_dir / "semantic_preserving_rejected_attempts.csv", rejected_rows)
    write_json(args.output_dir / "semantic_preserving_manifest.json", manifest)
    write_csv(args.output_dir / "semantic_preserving_lang_summary.csv", lang_summary)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
