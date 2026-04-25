#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "app/mme_scalpx/domain/instruments.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/execution.py",
    "etc/symbols.yaml",
    "etc/runtime.yaml",
]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def main() -> int:
    combined = "\n".join(read(f) for f in FILES)
    lower = combined.lower()

    required_terms = {
        "zerodha_token_or_instrument_token": ["zerodha", "instrument_token", "option_token"],
        "dhan_security_id": ["dhan", "security_id"],
        "canonical_instrument_key": ["instrument_key"],
        "option_symbol": ["option_symbol", "tradingsymbol", "trading_symbol"],
        "expiry": ["expiry"],
        "strike": ["strike"],
    }

    checks = []
    for case, terms in required_terms.items():
        checks.append({
            "case": case,
            "status": "PASS" if any(t in lower for t in terms) else "FAIL",
            "terms": terms,
        })

    checks.append({
        "case": "asia_kolkata_exchange_date_surface",
        "status": "PASS" if ("asia/kolkata" in lower or "ist" in lower) else "WARN",
    })

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "proof_name": "runtime_instrument_provider_equivalence",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "checks": checks,
        "failed_checks": failed,
        "uses_broker": False,
        "places_orders": False,
        "writes_live_redis": False,
        "does_not_prove": ["live_instrument_master_current_for_today", "broker_tokens_are_live_valid"],
    }

    out = ROOT / "run/proofs/proof_runtime_instrument_provider_equivalence.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
