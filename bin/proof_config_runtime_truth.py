#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "etc/runtime.yaml",
    "etc/config_registry.yaml",
    "etc/proof_registry.yaml",
    "etc/params_mme.yaml",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
]

REQUIRED_TEXT = {
    "app/mme_scalpx/main.py": [
        "provider_runtime",
        "SERVICE_REGISTRY",
        "FORBIDDEN_RUNTIME_PATHS",
    ],
    "app/mme_scalpx/core/settings.py": [
        "runtime",
        "trading",
    ],
    "etc/config_registry.yaml": [
        "runtime",
        "legacy",
    ],
}

FORBIDDEN_ACTIVE_CONFLICTS = [
    ("allow_live_orders: true", "allow_live_orders true is forbidden for final proof lane"),
    ("trading_enabled: true", "trading_enabled true is forbidden for final proof lane"),
    ("live_orders_allowed: true", "live_orders_allowed true is forbidden for final proof lane"),
]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def check_exists_nonempty(path: str) -> dict:
    p = ROOT / path
    return {
        "case": f"exists_nonempty:{path}",
        "status": "PASS" if p.exists() and p.stat().st_size > 0 else "FAIL",
        "path": path,
        "size": p.stat().st_size if p.exists() else 0,
    }

def main() -> int:
    checks = []

    for f in FILES:
        checks.append(check_exists_nonempty(f))

    for path, needles in REQUIRED_TEXT.items():
        text = read(path)
        for needle in needles:
            checks.append({
                "case": f"{path}:contains:{needle}",
                "status": "PASS" if needle in text else "FAIL",
                "path": path,
                "needle": needle,
            })

    combined = "\n".join(read(f) for f in FILES).lower()
    for needle, reason in FORBIDDEN_ACTIVE_CONFLICTS:
        checks.append({
            "case": f"forbidden_runtime_truth:{needle}",
            "status": "PASS" if needle.lower() not in combined else "FAIL",
            "reason": reason,
        })

    env_conflict_terms = ["SCALPX_", "MME_"]
    settings_text = read("app/mme_scalpx/core/settings.py")
    checks.append({
        "case": "settings_mentions_env_namespace_handling",
        "status": "PASS" if all(x in settings_text for x in env_conflict_terms) else "WARN",
        "note": "WARN means manual review needed for env conflict governance.",
    })

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "proof_name": "config_runtime_truth",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "does_not_prove": ["live_market_readiness", "broker_auth_validity"],
    }

    out = ROOT / "run/proofs/proof_config_runtime_truth.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
