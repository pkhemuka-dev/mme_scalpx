#!/usr/bin/env python3
from __future__ import annotations

import json
import time

from _batch25v_market_observation_common import (
    build_all_static_guard_report,
    hgetall_contract,
    proof_path,
    redis_client,
    required_constant,
    status_ready,
    unavailable_provider_report,
    write_proof,
)


def main() -> int:
    client = redis_client()
    const_name, key, provider = hgetall_contract(
        client,
        "HASH_STATE_PROVIDER_RUNTIME",
        "HASH_PROVIDER_RUNTIME",
    )

    _zn, zerodha = required_constant("PROVIDER_ZERODHA")
    _dn, dhan = required_constant("PROVIDER_DHAN")

    required_keys = (
        "futures_marketdata_provider_id",
        "selected_option_marketdata_provider_id",
        "option_context_provider_id",
        "execution_primary_provider_id",
        "futures_marketdata_status",
        "selected_option_marketdata_status",
        "option_context_status",
        "execution_primary_status",
    )

    runtime_mode = str(provider.get("family_runtime_mode", "observe_only")).strip().lower()
    provider_static = unavailable_provider_report()
    static_guard = build_all_static_guard_report()

    checks = {
        "provider_runtime_hash_present": bool(provider),
        "provider_runtime_required_keys_present": all(name in provider for name in required_keys),
        "futures_provider_allowed": provider.get("futures_marketdata_provider_id") in {zerodha, dhan},
        "selected_option_provider_is_dhan": provider.get("selected_option_marketdata_provider_id") == dhan,
        "option_context_provider_is_dhan": provider.get("option_context_provider_id") == dhan,
        "execution_primary_provider_is_zerodha": provider.get("execution_primary_provider_id") == zerodha,
        "futures_status_ready": status_ready(provider.get("futures_marketdata_status")),
        "selected_option_status_ready": status_ready(provider.get("selected_option_marketdata_status")),
        "option_context_status_ready": status_ready(provider.get("option_context_status")),
        "execution_primary_status_ready": status_ready(provider.get("execution_primary_status")),
        "observe_only_or_non_promoted_mode": runtime_mode in {"observe_only", "observe-only", "observe", ""},
        "provider_unavailable_does_not_become_ready": bool(provider_static.get("ok")),
        "static_guard_matrix_ok": bool(static_guard.get("ok")),
    }

    ok = all(checks.values())

    proof = {
        "proof_name": "proof_market_session_provider_runtime",
        "batch": "25V/26I",
        "generated_at_ns": time.time_ns(),
        "market_session_provider_runtime_ok": ok,
        "hash_constant": const_name,
        "hash_key": key,
        "checks": checks,
        "provider_runtime": provider,
        "static_guard_report": static_guard,
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    out = proof_path("proof_market_session_provider_runtime.json")
    write_proof(out, proof)
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
