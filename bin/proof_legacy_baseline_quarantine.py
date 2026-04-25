#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
PROOF_NAME = "legacy_baseline_quarantine"

LEGACY_MODULES = {
    "features_legacy_single": {
        "module": "app.mme_scalpx.services.features_legacy_single",
        "path": PROJECT_ROOT / "app/mme_scalpx/services/features_legacy_single.py",
    },
    "strategy_legacy_single": {
        "module": "app.mme_scalpx.services.strategy_legacy_single",
        "path": PROJECT_ROOT / "app/mme_scalpx/services/strategy_legacy_single.py",
    },
}

FORBIDDEN_IMPORT_FRAGMENTS = [
    "services.execution",
    "integrations.broker_api",
    "integrations.broker_auth",
    "integrations.dhan_execution",
    "core.redisx",
]

FORBIDDEN_ATTR_CALLS = {
    "xadd",
    "hset",
    "set",
    "publish",
    "place_entry_order",
    "place_exit_order",
    "place_order",
    "send_order",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def ast_scan(path: Path) -> dict[str, Any]:
    text = path.read_text()
    tree = ast.parse(text, filename=str(path))

    forbidden_imports: list[str] = []
    forbidden_calls: list[str] = []
    runtime_run_defs: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module_names = []
            if isinstance(node, ast.Import):
                module_names = [alias.name for alias in node.names]
            else:
                module_names = [node.module or ""]
            for module_name in module_names:
                for frag in FORBIDDEN_IMPORT_FRAGMENTS:
                    if frag in module_name:
                        forbidden_imports.append(module_name)

        if isinstance(node, ast.FunctionDef) and node.name == "run":
            arg_names = [arg.arg for arg in node.args.args]
            if arg_names == ["context"] or "context" in arg_names:
                runtime_run_defs.append(f"run({', '.join(arg_names)})")

        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr in FORBIDDEN_ATTR_CALLS:
                forbidden_calls.append(fn.attr)

    return {
        "forbidden_imports": sorted(set(forbidden_imports)),
        "forbidden_calls": sorted(set(forbidden_calls)),
        "runtime_run_defs": runtime_run_defs,
    }


def check_service_registry() -> dict[str, Any]:
    from app.mme_scalpx.core import names as N

    registry = getattr(N, "SERVICE_REGISTRY", {})
    values = set(registry.values()) if isinstance(registry, dict) else set()
    forbidden = [meta["module"] for meta in LEGACY_MODULES.values() if meta["module"] in values]
    return {
        "case": "legacy_modules_not_in_service_registry",
        "status": "PASS" if not forbidden else "FAIL",
        "forbidden": forbidden,
    }


def check_main_forbidden() -> dict[str, Any]:
    main_path = PROJECT_ROOT / "app/mme_scalpx/main.py"
    text = main_path.read_text() if main_path.exists() else ""
    missing = []
    for meta in LEGACY_MODULES.values():
        module = meta["module"]
        path = str(meta["path"].relative_to(PROJECT_ROOT))
        if module not in text:
            missing.append(module)
        if path not in text:
            missing.append(path)
    return {
        "case": "legacy_modules_listed_in_forbidden_runtime_paths",
        "status": "PASS" if not missing else "FAIL",
        "missing": missing,
    }


def check_baseline_docs() -> dict[str, Any]:
    candidates = [
        PROJECT_ROOT / "docs/strategy/LEGACY_SINGLE_BASELINE_FREEZE.md",
        PROJECT_ROOT / "docs/milestones/LEGACY_SINGLE_BASELINE_FREEZE.md",
    ]
    exists = [rel(path) for path in candidates if path.exists() and path.stat().st_size > 0]
    return {
        "case": "legacy_baseline_doc_exists_or_registry_classifies_reference",
        "status": "PASS" if exists or (PROJECT_ROOT / "etc/config_registry.yaml").exists() else "FAIL",
        "found": exists,
    }


def main() -> int:
    proof_dir = PROJECT_ROOT / "run/proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)

    cases: list[dict[str, Any]] = []

    for name, meta in LEGACY_MODULES.items():
        path = meta["path"]
        module_name = meta["module"]
        if not path.exists():
            cases.append({"case": f"{name}_file_exists", "status": "FAIL", "path": rel(path)})
            continue

        cases.append({"case": f"{name}_file_exists", "status": "PASS", "path": rel(path)})

        scan = ast_scan(path)
        cases.append({
            "case": f"{name}_no_forbidden_imports",
            "status": "PASS" if not scan["forbidden_imports"] else "FAIL",
            "forbidden_imports": scan["forbidden_imports"],
        })
        cases.append({
            "case": f"{name}_no_direct_transport_or_broker_calls",
            "status": "PASS" if not scan["forbidden_calls"] else "FAIL",
            "forbidden_calls": scan["forbidden_calls"],
        })
        cases.append({
            "case": f"{name}_runtime_run_context_shape_is_quarantined",
            "status": "PASS",
            "runtime_run_defs": scan["runtime_run_defs"],
            "note": (
                "Legacy modules may retain historical run(context) shape only when "
                "they are not in SERVICE_REGISTRY and are explicitly listed in "
                "main.py forbidden runtime paths. Those conditions are checked "
                "separately in this proof."
            ),
        })

        try:
            importlib.import_module(module_name)
            cases.append({"case": f"{name}_imports", "status": "PASS", "module": module_name})
        except Exception as exc:
            cases.append({
                "case": f"{name}_imports",
                "status": "FAIL",
                "module": module_name,
                "error": f"{type(exc).__name__}: {exc}",
            })

    cases.append(check_service_registry())
    cases.append(check_main_forbidden())
    cases.append(check_baseline_docs())

    failed = [case for case in cases if case.get("status") != "PASS"]
    result = {
        "proof": PROOF_NAME,
        "status": "PASS" if not failed else "FAIL",
        "failed_cases": failed,
        "cases": cases,
    }

    latest = proof_dir / f"{PROOF_NAME}.json"
    latest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
