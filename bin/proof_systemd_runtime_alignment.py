#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REGISTRY_PATH = Path("docs/systemd_runtime_unit_registry.md")

SECRET_PATTERNS = re.compile(
    r"(access_token|refresh_token|client_secret|api_secret|api_key|authorization|bearer\s+|password|passwd|pin|totp|jwt|enctoken)",
    re.IGNORECASE,
)


def no_secrets_in_text(text: str) -> tuple[bool, list[str]]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and SECRET_PATTERNS.search(stripped):
            hits.append(f"{lineno}:{stripped[:120]}")
    return (not hits, hits)


def main() -> int:
    generated_at_ns = time.time_ns()
    checks: dict[str, bool] = {}
    errors: list[str] = []

    if not REGISTRY_PATH.exists():
        raise SystemExit(f"Missing registry: {REGISTRY_PATH}")

    text = REGISTRY_PATH.read_text(encoding="utf-8")

    checks["registry_exists"] = True
    checks["startup_order_feeds_features_strategy"] = "1. feeds" in text and "2. features" in text and "3. strategy" in text
    checks["risk_execution_independent_health_linked"] = (
        "risk and execution are independently started but health-linked" in text
        and "execution must respect risk state for entries" in text
        and "risk must not block exits" in text
    )
    checks["monitor_report_read_only"] = "monitor is control/observability only" in text and "report is read-only reconstruction" in text
    checks["execution_lock_ownership_explicit"] = (
        "execution owns execution lock" in text
        and "feeds/features/strategy/risk/monitor/report do not own execution lock" in text
    )
    checks["provider_role_law_documented"] = (
        "futures marketdata preferred provider = ZERODHA" in text
        and "selected option marketdata provider = DHAN" in text
        and "option context provider = DHAN" in text
        and "execution primary provider = ZERODHA" in text
    )
    checks["dhan_depth_honesty_documented"] = (
        "configured target = TOP20_ENHANCED" in text
        and "runtime active mode must not claim TOP20_ENHANCED unless runtime activation proof exists" in text
        and "FULL_TOP5_BASE" in text
    )
    checks["observe_only_hold_only_documented"] = (
        "rollout_mode = observe_only" in text
        and "strategy_publish_mode = HOLD_ONLY" in text
        and "broker_orders_allowed = false" in text
    )

    no_secret_values, secret_hits = no_secrets_in_text(text)
    checks["no_secret_values_in_systemd_registry"] = no_secret_values
    if secret_hits:
        errors.extend(f"secret_like_registry_value:{hit}" for hit in secret_hits)

    proof_ok = all(checks.values()) and not errors

    proof = {
        "proof_name": "proof_systemd_runtime_alignment",
        "batch": "25S",
        "generated_at_ns": generated_at_ns,
        "systemd_runtime_alignment_ok": proof_ok,
        "systemd_service_registry_ok": proof_ok,
        "checks": checks,
        "errors": errors,
        "registry_path": str(REGISTRY_PATH),
    }

    out = Path("run/proofs/proof_systemd_runtime_alignment.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "systemd_runtime_alignment_ok": proof_ok,
        "systemd_service_registry_ok": proof_ok,
        "startup_order_feeds_features_strategy": checks["startup_order_feeds_features_strategy"],
        "execution_lock_ownership_explicit": checks["execution_lock_ownership_explicit"],
        "monitor_report_read_only": checks["monitor_report_read_only"],
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
