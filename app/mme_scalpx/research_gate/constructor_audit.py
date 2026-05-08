# RAW-U deep constructor audit helpers.

from __future__ import annotations

import ast
import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TRADE_KEYS = {
    "row_kind",
    "artifact_kind",
    "trade_id",
    "candidate_id",
    "event_id",
    "source_run_id",
    "closed_trade_truth",
    "candidate_vs_executed",
    "entry_ts",
    "exit_ts",
    "entry_price",
    "exit_price",
    "qty",
    "gross_pnl",
    "net_pnl_after_costs",
    "costs",
    "exit_reason",
    "decision_action",
    "action",
    "family",
    "side",
    "strategy_id",
    "source_artifact",
}


@dataclass(frozen=True)
class ConstructorSite:
    path: str
    function_name: str
    lineno: int
    end_lineno: int
    col_offset: int
    end_col_offset: int
    keys: tuple[str, ...]
    score: int
    source_preview: str


def string_key(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def function_stack_for(tree: ast.AST) -> dict[int, str]:
    mapping: dict[int, str] = {}

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Dict(self, node: ast.Dict) -> Any:
            mapping[id(node)] = ".".join(self.stack) if self.stack else "<module>"
            self.generic_visit(node)

    Visitor().visit(tree)
    return mapping


def is_eligible_dict(node: ast.Dict) -> tuple[bool, tuple[str, ...], int]:
    keys = tuple(k for k in (string_key(key) for key in node.keys) if k)
    lowered = {k.lower() for k in keys}
    overlap = sorted(lowered & TRADE_KEYS)
    score = len(overlap)

    hard_keys = {
        "trade_id",
        "closed_trade_truth",
        "candidate_vs_executed",
        "net_pnl_after_costs",
        "gross_pnl",
        "entry_price",
        "exit_price",
        "decision_action",
        "candidate_id",
        "event_id",
    }
    eligible = score >= 2 or bool(lowered & hard_keys)
    return eligible, tuple(sorted(overlap)), score


def audit_constructor_sites(path: str | Path) -> list[ConstructorSite]:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text)
    function_map = function_stack_for(tree)
    sites: list[ConstructorSite] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            continue
        eligible, keys, score = is_eligible_dict(node)
        if not eligible:
            continue
        preview = ast.get_source_segment(text, node) or ""
        if "_raw_u_emit_constructor" in preview or "raw_u_constructor_family_emission_applied" in preview:
            continue
        sites.append(
            ConstructorSite(
                path=str(p),
                function_name=function_map.get(id(node), "<unknown>"),
                lineno=int(node.lineno),
                end_lineno=int(node.end_lineno),
                col_offset=int(node.col_offset),
                end_col_offset=int(node.end_col_offset),
                keys=keys,
                score=score,
                source_preview=preview[:500].replace("\n", "\\n"),
            )
        )

    sites.sort(key=lambda s: (s.path, s.lineno, s.col_offset))
    return sites


def _offset(lines: list[str], lineno: int, col: int) -> int:
    return sum(len(line) for line in lines[: lineno - 1]) + col


def insertion_offset_after_docstring_future_imports(text: str) -> int:
    try:
        tree = ast.parse(text)
        lines = text.splitlines(True)
        end_line = 0
        body = list(tree.body)
        idx = 0
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
            end_line = max(end_line, int(getattr(body[0], "end_lineno", 0) or 0))
            idx = 1
        while idx < len(body):
            node = body[idx]
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                end_line = max(end_line, int(getattr(node, "end_lineno", 0) or 0))
                idx += 1
                continue
            break
        return sum(len(line) for line in lines[:end_line])
    except SyntaxError:
        return 0


HOOK_BLOCK = (
    "\n# RAW-U constructor family emission hook -- replay-only, non-live.\n"
    "try:\n"
    "    from app.mme_scalpx.replay.raw_constructor_family_emit import emit_constructor_family as _raw_u_emit_constructor_family\n"
    "except Exception:\n"
    "    def _raw_u_emit_constructor_family(value, *, source_artifact='', constructor_name=''):\n"
    "        return value\n"
    "\n\n"
    "def _raw_u_emit_constructor(value, *, constructor_name=''):\n"
    "    return _raw_u_emit_constructor_family(value, source_artifact=__file__, constructor_name=constructor_name)\n"
    "# END RAW-U constructor family emission hook.\n"
)


def patch_constructor_sites(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    original = text
    sites = audit_constructor_sites(p)

    if sites and "RAW-U constructor family emission hook" not in text:
        pos = insertion_offset_after_docstring_future_imports(text)
        text = text[:pos] + HOOK_BLOCK + text[pos:]
        p.write_text(text, encoding="utf-8")
        text = p.read_text(encoding="utf-8", errors="replace")
        sites = audit_constructor_sites(p)

    lines = text.splitlines(True)
    replacements: list[tuple[int, int, str, ConstructorSite]] = []

    for site in sites:
        start = _offset(lines, site.lineno, site.col_offset)
        end = _offset(lines, site.end_lineno, site.end_col_offset)
        segment = text[start:end]
        if "_raw_u_emit_constructor" in segment:
            continue
        constructor_name = f"{site.function_name}@{site.lineno}"
        wrapped = f"_raw_u_emit_constructor({segment}, constructor_name={constructor_name!r})"
        replacements.append((start, end, wrapped, site))

    for start, end, wrapped, _site in sorted(replacements, key=lambda x: x[0], reverse=True):
        text = text[:start] + wrapped + text[end:]

    p.write_text(text, encoding="utf-8")

    return {
        "path": str(p),
        "constructor_sites_detected": len(sites),
        "constructor_sites_patched": len(replacements),
        "patched": text != original,
        "sites": [
            {
                "function_name": site.function_name,
                "lineno": site.lineno,
                "end_lineno": site.end_lineno,
                "keys": list(site.keys),
                "score": site.score,
                "source_preview": site.source_preview,
            }
            for _start, _end, _wrapped, site in replacements
        ],
    }


def write_sites_csv(path: str | Path, patch_results: list[dict[str, Any]]) -> None:
    fieldnames = ["path", "function_name", "lineno", "end_lineno", "score", "keys", "source_preview"]
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in patch_results:
            for site in result.get("sites", []):
                writer.writerow({
                    "path": result.get("path", ""),
                    "function_name": site.get("function_name", ""),
                    "lineno": site.get("lineno", ""),
                    "end_lineno": site.get("end_lineno", ""),
                    "score": site.get("score", ""),
                    "keys": ",".join(site.get("keys", [])),
                    "source_preview": site.get("source_preview", ""),
                })


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, p)
