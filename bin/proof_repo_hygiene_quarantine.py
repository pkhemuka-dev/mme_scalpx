#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_ROOTS = [PROJECT_ROOT / "app", PROJECT_ROOT / "bin"]

LEGACY_MODULES = [
    PROJECT_ROOT / "app/mme_scalpx/services/features_legacy_single.py",
    PROJECT_ROOT / "app/mme_scalpx/services/strategy_legacy_single.py",
]

FORBIDDEN_MODULE_STRINGS = [
    "app.mme_scalpx.services.features_legacy_single",
    "app.mme_scalpx.services.strategy_legacy_single",
    "app/mme_scalpx/services/features_legacy_single.py",
    "app/mme_scalpx/services/strategy_legacy_single.py",
]

PROOF_NAME = "repo_hygiene_quarantine"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def find_hygiene_violations() -> list[str]:
    violations: list[str] = []
    for root in ACTIVE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            name = path.name
            if name == "__pycache__":
                violations.append(rel(path))
            elif name.endswith(".pyc"):
                violations.append(rel(path))
            elif ".bak" in name or name.endswith(".bak") or ".bak_" in name:
                violations.append(rel(path))
    return sorted(set(violations))


def check_legacy_headers() -> list[dict[str, Any]]:
    cases = []
    for path in LEGACY_MODULES:
        exists = path.exists()
        text = path.read_text() if exists else ""
        ok = exists and "LEGACY BASELINE MODULE — NOT A LIVE RUNTIME SERVICE" in text
        cases.append({
            "case": f"legacy_header_present:{rel(path)}",
            "status": "PASS" if ok else "FAIL",
            "exists": exists,
        })
    return cases


def check_main_forbidden_paths() -> dict[str, Any]:
    main_path = PROJECT_ROOT / "app/mme_scalpx/main.py"
    text = main_path.read_text() if main_path.exists() else ""
    missing = [item for item in FORBIDDEN_MODULE_STRINGS if item not in text]
    return {
        "case": "legacy_service_files_forbidden_in_main",
        "status": "PASS" if not missing else "FAIL",
        "missing": missing,
    }


def check_config_registry() -> dict[str, Any]:
    path = PROJECT_ROOT / "etc/config_registry.yaml"
    text = path.read_text() if path.exists() else ""
    required = [
        "features_legacy_single.py",
        "strategy_legacy_single.py",
        "REFERENCE_BASELINE",
        "runtime_service_allowed: false",
        "runtime_load_allowed: false",
    ]
    missing = [item for item in required if item not in text]
    return {
        "case": "config_registry_classifies_legacy",
        "status": "PASS" if not missing else "FAIL",
        "missing": missing,
        "path": rel(path),
    }


def check_docs() -> list[dict[str, Any]]:
    docs = [
        PROJECT_ROOT / "docs/contracts/compatibility_alias_registry.md",
        PROJECT_ROOT / "docs/systemd_runtime_unit_registry.md",
    ]
    cases = []
    for path in docs:
        cases.append({
            "case": f"doc_exists:{rel(path)}",
            "status": "PASS" if path.exists() and path.stat().st_size > 0 else "FAIL",
            "path": rel(path),
        })
    return cases


def main() -> int:
    proof_dir = PROJECT_ROOT / "run/proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)

    hygiene_violations = find_hygiene_violations()
    cases: list[dict[str, Any]] = []

    cases.append({
        "case": "no_bak_pyc_pycache_under_active_roots",
        "status": "PASS" if not hygiene_violations else "FAIL",
        "violations": hygiene_violations[:200],
        "violation_count": len(hygiene_violations),
    })
    cases.extend(check_legacy_headers())
    cases.append(check_main_forbidden_paths())
    cases.append(check_config_registry())
    cases.extend(check_docs())

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
