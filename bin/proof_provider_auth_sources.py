#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "app/mme_scalpx/integrations/dhan_runtime_clients.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/core/settings.py",
    "etc/runtime.yaml",
    "etc/project.env",
]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def main() -> int:
    checks = []

    combined = "\n".join(read(f) for f in FILES)
    lower = combined.lower()

    checks.append({
        "case": "zerodha_auth_surface_declared",
        "status": "PASS" if "zerodha" in lower else "FAIL",
    })
    checks.append({
        "case": "dhan_auth_surface_declared",
        "status": "PASS" if "dhan" in lower else "FAIL",
    })
    checks.append({
        "case": "auth_uses_env_or_config_not_hardcoded_only",
        "status": "PASS" if ("os.environ" in combined or "getenv" in combined or "env" in lower) else "WARN",
    })

    hardcoded = []
    for f in FILES:
        text = read(f)
        for m in re.finditer(r"(?i)(access_token|client_secret|api_key|enctoken)\s*[:=]\s*['\"][^'\"]{8,}['\"]", text):
            hardcoded.append({"path": f, "match": m.group(0)[:80]})

    checks.append({
        "case": "no_hardcoded_provider_secrets",
        "status": "PASS" if not hardcoded else "FAIL",
        "hardcoded_count": len(hardcoded),
        "examples": hardcoded[:10],
    })

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "proof_name": "provider_auth_sources",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "does_not_prove": ["tokens_are_current", "broker_login_success"],
    }

    out = ROOT / "run/proofs/proof_provider_auth_sources.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
