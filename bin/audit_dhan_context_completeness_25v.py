#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from bin._batch25v_market_observation_common import hgetall_contract, redis_client


def _loads_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    s = str(value).strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        return ast.literal_eval(s)
    except Exception:
        return None


def _non_empty_mapping(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value)


def main() -> int:
    client = redis_client()
    now_ns = time.time_ns()

    provider_const, provider_key, provider = hgetall_contract(
        client,
        "HASH_STATE_PROVIDER_RUNTIME",
        "HASH_PROVIDER_RUNTIME",
    )
    context_const, context_key, context = hgetall_contract(
        client,
        "HASH_STATE_DHAN_CONTEXT",
        "HASH_DHAN_CONTEXT",
    )

    ts_raw = context.get("last_update_ns") or context.get("ts_event_ns") or context.get("ts_frame_ns")
    context_age_ms = None
    if ts_raw:
        try:
            context_age_ms = round((now_ns - int(ts_raw)) / 1_000_000, 2)
        except Exception:
            context_age_ms = None

    option_chain_ladder = _loads_json(context.get("option_chain_ladder_json"))
    strike_ladder = _loads_json(context.get("strike_ladder_json"))
    oi_wall_summary = _loads_json(context.get("oi_wall_summary_json"))
    selected_call_context = _loads_json(context.get("selected_call_context_json"))
    selected_put_context = _loads_json(context.get("selected_put_context_json"))

    if not isinstance(option_chain_ladder, list):
        option_chain_ladder = []
    if not isinstance(strike_ladder, list):
        strike_ladder = []

    oi_wall_present = bool(isinstance(oi_wall_summary, Mapping) and oi_wall_summary.get("present"))
    oi_wall_ladder_size = None
    if isinstance(oi_wall_summary, Mapping):
        oi_wall_ladder_size = oi_wall_summary.get("ladder_size")

    checks = {
        "provider_runtime_fresh": (provider.get("transition_reason") != "BOOTSTRAP"),
        "futures_marketdata_healthy": provider.get("futures_marketdata_status") == "HEALTHY",
        "selected_option_marketdata_healthy": provider.get("selected_option_marketdata_status") == "HEALTHY",
        "option_context_status_healthy": provider.get("option_context_status") == "HEALTHY",
        "context_hash_present": bool(context),
        "context_hash_fresh_under_5s": context_age_ms is not None and context_age_ms <= 5000,
        "context_status_healthy": context.get("context_status") == "HEALTHY",
        "option_chain_ladder_non_empty": len(option_chain_ladder) > 0,
        "strike_ladder_non_empty": len(strike_ladder) > 0,
        "oi_wall_summary_present": oi_wall_present,
        "selected_call_context_non_empty": _non_empty_mapping(selected_call_context),
        "selected_put_context_non_empty": _non_empty_mapping(selected_put_context),
        "selected_call_key_present": bool(str(context.get("selected_call_instrument_key") or "").strip()),
        "selected_put_key_present": bool(str(context.get("selected_put_instrument_key") or "").strip()),
    }

    blockers = {
        key: value
        for key, value in checks.items()
        if value is not True
    }

    proof = {
        "proof_name": "proof_batch25v_dhan_context_completeness_audit",
        "generated_at_ns": now_ns,
        "dhan_context_completeness_ready": (
            checks["option_context_status_healthy"]
            and checks["context_status_healthy"]
            and checks["option_chain_ladder_non_empty"]
            and checks["strike_ladder_non_empty"]
            and checks["selected_call_context_non_empty"]
            and checks["selected_put_context_non_empty"]
            and checks["oi_wall_summary_present"]
        ),
        "provider_runtime": {
            "const": provider_const,
            "key": provider_key,
            "futures_marketdata_status": provider.get("futures_marketdata_status"),
            "selected_option_marketdata_status": provider.get("selected_option_marketdata_status"),
            "option_context_status": provider.get("option_context_status"),
            "execution_primary_status": provider.get("execution_primary_status"),
            "transition_reason": provider.get("transition_reason"),
            "provider_transition_seq": provider.get("provider_transition_seq"),
            "message": provider.get("message"),
        },
        "dhan_context": {
            "const": context_const,
            "key": context_key,
            "field_count": len(context),
            "age_ms": context_age_ms,
            "context_status": context.get("context_status"),
            "provider_id": context.get("provider_id"),
            "atm_strike": context.get("atm_strike"),
            "selected_call_instrument_key": context.get("selected_call_instrument_key"),
            "selected_put_instrument_key": context.get("selected_put_instrument_key"),
            "option_chain_ladder_len": len(option_chain_ladder),
            "strike_ladder_len": len(strike_ladder),
            "oi_wall_summary_present": oi_wall_present,
            "oi_wall_summary_ladder_size": oi_wall_ladder_size,
            "selected_call_context_keys": sorted(selected_call_context.keys()) if isinstance(selected_call_context, Mapping) else [],
            "selected_put_context_keys": sorted(selected_put_context.keys()) if isinstance(selected_put_context, Mapping) else [],
            "selected_call_score": context.get("selected_call_score"),
            "selected_put_score": context.get("selected_put_score"),
        },
        "checks": checks,
        "blockers": blockers,
        "proof_path": "run/proofs/proof_batch25v_dhan_context_completeness_audit.json",
    }

    Path("run/proofs/proof_batch25v_dhan_context_completeness_audit.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
