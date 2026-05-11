#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N  # noqa: E402

PROOF_NAME = "names_alias_lifecycle"

ALLOWED_STATUS = {
    "permanent_compatibility_alias",
    "temporary_migration_alias",
    "deprecated_alias",
    "forbidden_for_new_code",
}

REGISTRY_PATH = PROJECT_ROOT / "docs/contracts/compatibility_alias_registry.md"

ALIASES_TO_CHECK = [
    "STREAM_CMD",
    "STREAM_DECISIONS",
    "STREAM_ORDERS",
    "STREAM_FEATURES",
    "STATE_FEATURES",
    "STATE_POSITION",
    "HB_FEATURES",
    "GROUP_EXEC",
    "LOCK_EXECUTION",
    "EXEC_MODE_NORMAL",
    "HEALTH_OK",
]


def parse_registry() -> dict[str, dict[str, str]]:
    if not REGISTRY_PATH.exists():
        return {}

    rows: dict[str, dict[str, str]] = {}
    for line in REGISTRY_PATH.read_text().splitlines():
        if not line.startswith("|"):
            continue

        normalized = line.strip().lower()

        # Skip only the markdown header row and separator row.
        # Do NOT skip data rows containing values like temporary_migration_alias.
        if normalized.startswith("| alias |") or normalized.startswith("|---"):
            continue

        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue

        alias, target, status, new_code_allowed, owner, removal_condition = parts[:6]
        if not re.match(r"^[A-Z0-9_]+$", alias):
            continue

        rows[alias] = {
            "target": target,
            "status": status,
            "new_code_allowed": new_code_allowed,
            "owner": owner,
            "removal_condition": removal_condition,
        }

    return rows


def main() -> int:
    proof_dir = PROJECT_ROOT / "run/proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)

    registry = parse_registry()
    cases: list[dict[str, Any]] = []

    for alias in ALIASES_TO_CHECK:
        if not hasattr(N, alias):
            cases.append(
                {
                    "case": f"alias_absent_skip:{alias}",
                    "status": "PASS",
                    "skipped": True,
                    "reason": "alias not present in names.py",
                }
            )
            continue

        row = registry.get(alias)
        if not row:
            cases.append(
                {
                    "case": f"alias_registered:{alias}",
                    "status": "FAIL",
                    "reason": "missing registry row",
                }
            )
            continue

        target = row["target"]
        status = row["status"]
        new_code_allowed = row["new_code_allowed"].lower()

        target_exists = hasattr(N, target)
        value_match = target_exists and getattr(N, alias) == getattr(N, target)

        cases.extend(
            [
                {
                    "case": f"alias_target_exists:{alias}",
                    "status": "PASS" if target_exists else "FAIL",
                    "target": target,
                },
                {
                    "case": f"alias_value_matches_target:{alias}",
                    "status": "PASS" if value_match else "FAIL",
                    "target": target,
                },
                {
                    "case": f"alias_status_allowed:{alias}",
                    "status": "PASS" if status in ALLOWED_STATUS else "FAIL",
                    "status_value": status,
                },
                {
                    "case": f"alias_new_code_allowed_boolean:{alias}",
                    "status": "PASS" if new_code_allowed in {"true", "false"} else "FAIL",
                    "new_code_allowed": row["new_code_allowed"],
                },
                {
                    "case": f"alias_owner_present:{alias}",
                    "status": "PASS" if bool(row["owner"]) else "FAIL",
                    "owner": row["owner"],
                },
                {
                    "case": f"alias_removal_condition_present:{alias}",
                    "status": "PASS" if bool(row["removal_condition"]) else "FAIL",
                    "removal_condition": row["removal_condition"],
                },
            ]
        )

    failed = [case for case in cases if case.get("status") != "PASS"]

    result = {
        "proof": PROOF_NAME,
        "status": "PASS" if not failed else "FAIL",
        "registry_path": str(REGISTRY_PATH.relative_to(PROJECT_ROOT)),
        "failed_cases": failed,
        "cases": cases,
    }

    latest = proof_dir / f"{PROOF_NAME}.json"
    latest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
