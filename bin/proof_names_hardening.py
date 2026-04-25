#!/usr/bin/env python3
from __future__ import annotations

"""
Proof: names.py institutional hardening.

This proof validates the live source tree, not archived audit bundles.
It intentionally excludes:
- run/audit_bundle_* copied evidence
- run/_code_backups
- generated proof JSON
- this proof's own stale-literal definitions
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N


ROOT = PROJECT_ROOT

STALE_LITERALS = (
    "state:" + "dhan:context",
    "state:" + "dhan_context",
    "state:" + "option_confirm",
    "state:" + "provider_runtime",
)

REQUIRED_ALIAS_KEYS = (
    "STREAM_CMD",
    "STREAM_DECISIONS",
    "STREAM_ORDERS",
    "STREAM_FEATURES",
    "STATE_DHAN_CONTEXT",
    "STATE_PROVIDER_RUNTIME",
    "GROUP_EXEC",
    "GROUP_FEATURES_FUT",
    "GROUP_FEATURES_OPT",
    "LOCK_EXECUTION",
    "EXEC_MODE_NORMAL",
    "HEALTH_OK",
)

EXCLUDED_PREFIXES = (
    ".venv/",
    "run/_code_backups/",
    "run/audit_bundle_",
    "run/proofs/",
)

EXCLUDED_FILES = {
    "app/mme_scalpx/core/names.py",
    "bin/proof_names_hardening.py",
    "bin/proof_redis_contract_matrix.py",
}


def _is_excluded(rel: str) -> bool:
    return rel in EXCLUDED_FILES or any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def _failures_for_stale_literals() -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []

    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()

        if "__pycache__" in rel or _is_excluded(rel):
            continue

        text = path.read_text(errors="replace")
        for literal in STALE_LITERALS:
            if literal in text:
                failures.append({"file": rel, "literal": literal})

    return failures


def _check_bootstrap_groups() -> list[str]:
    failures: list[str] = []
    path = ROOT / "ops" / "bootstrap_groups.py"
    if not path.exists():
        return ["ops/bootstrap_groups.py missing"]

    text = path.read_text(errors="replace")

    if "N.get_group_specs" not in text and "names.get_group_specs" not in text:
        failures.append("ops/bootstrap_groups.py does not consume names.get_group_specs()")

    if re.search(r"^\s*LIVE_GROUP_SPECS\s*=", text, flags=re.MULTILINE):
        failures.append("ops/bootstrap_groups.py still defines local LIVE_GROUP_SPECS")

    if re.search(r"^\s*REPLAY_GROUP_SPECS\s*=", text, flags=re.MULTILINE):
        failures.append("ops/bootstrap_groups.py still defines local REPLAY_GROUP_SPECS")

    return failures


def _check_alias_registry() -> list[str]:
    failures: list[str] = []
    registry = N.get_compatibility_alias_registry()

    for key in REQUIRED_ALIAS_KEYS:
        if key not in registry:
            failures.append(f"missing alias registry key: {key}")

    return failures


def _check_forbidden_modules() -> list[str]:
    failures: list[str] = []

    forbidden = N.get_forbidden_runtime_modules()
    service_modules = {
        service_def.module_path for service_def in N.SERVICE_REGISTRY.values()
    }

    for module_path, meta in forbidden.items():
        if module_path in service_modules:
            failures.append(f"forbidden module is in SERVICE_REGISTRY: {module_path}")
        if meta.replacement_module_path and meta.replacement_module_path not in service_modules:
            failures.append(
                f"forbidden module replacement is not registered: "
                f"{module_path} -> {meta.replacement_module_path}"
            )

    main_path = ROOT / "app" / "mme_scalpx" / "main.py"
    if main_path.exists():
        main_text = main_path.read_text(errors="replace")
        if "get_forbidden_runtime_paths()" not in main_text:
            failures.append("main.py does not consume names.get_forbidden_runtime_paths()")

    return failures


def main() -> int:
    failures: list[str | dict[str, str]] = []

    try:
        N.validate_names_contract()
    except Exception as exc:
        failures.append(f"validate_names_contract failed: {exc!r}")

    try:
        N.validate_names_hardening_contract()
    except Exception as exc:
        failures.append(f"validate_names_hardening_contract failed: {exc!r}")

    failures.extend(_check_alias_registry())
    failures.extend(_check_forbidden_modules())
    failures.extend(_check_bootstrap_groups())
    failures.extend(_failures_for_stale_literals())

    proof = {
        "proof": "names_institutional_hardening",
        "status": "FAIL" if failures else "PASS",
        "families": tuple(N.STRATEGY_FAMILY_IDS),
        "providers": tuple(N.PROVIDER_IDS),
        "live_group_specs": N.get_group_specs(replay=False),
        "replay_group_specs": N.get_group_specs(replay=True),
        "forbidden_runtime_modules": tuple(N.get_forbidden_runtime_modules().keys()),
        "alias_registry_count": len(N.get_compatibility_alias_registry()),
        "failures": failures,
    }

    out = ROOT / "run" / "proofs" / "names_institutional_hardening.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
