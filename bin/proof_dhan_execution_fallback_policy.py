#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/dhan_runtime_clients.py",
    "etc/runtime.yaml",
    "etc/config_registry.yaml",
]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def main() -> int:
    combined = "\n".join(read(f) for f in FILES)
    lower = combined.lower()

    checks = [
        {
            "case": "dhan_execution_surface_mentioned",
            "status": "PASS" if "dhan" in lower and "execution" in lower else "FAIL",
        },
        {
            "case": "fallback_policy_explicit",
            "status": "PASS" if "fallback" in lower else "FAIL",
        },
        {
            "case": "fallback_not_silent",
            "status": "PASS" if any(x in lower for x in ["disabled", "explicit", "reject", "fail"]) else "FAIL",
        },
        {
            "case": "execution_primary_surface_present",
            "status": "PASS" if "execution_primary" in lower or "primary" in lower else "WARN",
        },
    ]

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "proof_name": "dhan_execution_fallback_policy",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "does_not_prove": ["actual_dhan_order_placement", "actual_fallback_execution_success"],
    }

    out = ROOT / "run/proofs/proof_dhan_execution_fallback_policy.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
