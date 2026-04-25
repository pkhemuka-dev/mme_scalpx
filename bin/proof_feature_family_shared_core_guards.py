#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = ROOT / "run" / "proofs" / "feature_family_shared_core_guards.json"

def ok(name: str, condition: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"name": name, "ok": bool(condition), "details": details or {}}
    if not condition:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

def main() -> int:
    sys.path.insert(0, str(ROOT))

    from app.mme_scalpx.core import names as N
    from app.mme_scalpx.services.feature_family import common as C
    from app.mme_scalpx.services.feature_family import contracts as K
    from app.mme_scalpx.services.feature_family import futures_core as F
    from app.mme_scalpx.services.feature_family import option_core as O
    from app.mme_scalpx.services.feature_family import regime as R
    from app.mme_scalpx.services.feature_family import strike_selection as S
    from app.mme_scalpx.services.feature_family import tradability as T

    cases: list[dict[str, Any]] = []

    provider_block = C.build_provider_runtime_block()
    cases.append(ok(
        "common_provider_runtime_defaults_fail_closed",
        provider_block["active_futures_provider_id"] is None
        and provider_block["active_selected_option_provider_id"] is None
        and provider_block["active_option_context_provider_id"] is None
        and provider_block["active_execution_provider_id"] is None
        and provider_block["fallback_execution_provider_id"] is None
        and provider_block["futures_provider_status"] == N.PROVIDER_STATUS_UNAVAILABLE
        and provider_block["selected_option_provider_status"] == N.PROVIDER_STATUS_UNAVAILABLE
        and provider_block["option_context_provider_status"] == N.PROVIDER_STATUS_UNAVAILABLE,
        provider_block,
    ))

    cases.append(ok(
        "common_classic_missing_runtime_mode_not_ready",
        C.derive_provider_ready_classic(
            active_futures_provider_id=N.PROVIDER_ZERODHA,
            active_selected_option_provider_id=N.PROVIDER_DHAN,
            strategy_runtime_mode=None,
            futures_provider_status=N.PROVIDER_STATUS_HEALTHY,
            selected_option_provider_status=N.PROVIDER_STATUS_HEALTHY,
        ) is False,
    ))

    cases.append(ok(
        "common_classic_unavailable_status_not_ready",
        C.derive_provider_ready_classic(
            active_futures_provider_id=N.PROVIDER_ZERODHA,
            active_selected_option_provider_id=N.PROVIDER_DHAN,
            strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_NORMAL,
            futures_provider_status=N.PROVIDER_STATUS_UNAVAILABLE,
            selected_option_provider_status=N.PROVIDER_STATUS_HEALTHY,
        ) is False,
    ))

    cases.append(ok(
        "common_classic_healthy_statuses_ready",
        C.derive_provider_ready_classic(
            active_futures_provider_id=N.PROVIDER_ZERODHA,
            active_selected_option_provider_id=N.PROVIDER_DHAN,
            strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_NORMAL,
            futures_provider_status=N.PROVIDER_STATUS_HEALTHY,
            selected_option_provider_status=N.PROVIDER_STATUS_HEALTHY,
        ) is True,
    ))

    cases.append(ok(
        "common_miso_context_ready_required",
        C.derive_provider_ready_miso(
            active_futures_provider_id=N.PROVIDER_DHAN,
            active_selected_option_provider_id=N.PROVIDER_DHAN,
            active_option_context_provider_id=N.PROVIDER_DHAN,
            strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
            futures_provider_status=N.PROVIDER_STATUS_HEALTHY,
            selected_option_provider_status=N.PROVIDER_STATUS_HEALTHY,
            option_context_provider_status=N.PROVIDER_STATUS_HEALTHY,
            dhan_context_ready=False,
        ) is False,
    ))

    cases.append(ok(
        "common_miso_context_ready_passes",
        C.derive_provider_ready_miso(
            active_futures_provider_id=N.PROVIDER_DHAN,
            active_selected_option_provider_id=N.PROVIDER_DHAN,
            active_option_context_provider_id=N.PROVIDER_DHAN,
            strategy_runtime_mode=N.STRATEGY_RUNTIME_MODE_BASE_5DEPTH,
            futures_provider_status=N.PROVIDER_STATUS_HEALTHY,
            selected_option_provider_status=N.PROVIDER_STATUS_HEALTHY,
            option_context_provider_status=N.PROVIDER_STATUS_HEALTHY,
            dhan_context_ready=True,
        ) is True,
    ))

    fut_zero = F.build_futures_surface(
        futures_surface={
            "instrument_key": "NIFTY-FUT",
            "ltp": 0,
            "ts_event_ns": 1,
        },
        runtime_mode="NORMAL",
        source_label="proof",
        role_label="proof",
    )
    cases.append(ok(
        "futures_ltp_zero_not_live_present",
        fut_zero["present"] is False and fut_zero["quote_present"] is False,
        fut_zero,
    ))

    fut_meta_only = F.build_futures_surface(
        futures_surface={"instrument_key": "NIFTY-FUT"},
        runtime_mode="NORMAL",
        source_label="proof",
        role_label="proof",
    )
    cases.append(ok(
        "futures_instrument_only_not_live_present",
        fut_meta_only["present"] is False
        and fut_meta_only["metadata_present"] is True
        and fut_meta_only["fresh"] is False,
        fut_meta_only,
    ))

    fut_good = F.build_futures_surface(
        futures_surface={
            "instrument_key": "NIFTY-FUT",
            "ltp": 22500,
            "best_bid": 22499.5,
            "best_ask": 22500.5,
            "bid_qty_5": 100,
            "ask_qty_5": 120,
            "ts_event_ns": 1,
        },
        runtime_mode="NORMAL",
        source_label="proof",
        role_label="proof",
    )
    cases.append(ok(
        "futures_live_quote_present_passes",
        fut_good["present"] is True
        and fut_good["live_present"] is True
        and fut_good["fresh"] is True,
        fut_good,
    ))

    opt_strike_only = O.build_live_option_surface(
        side=N.SIDE_CALL,
        live_source={},
        strike=22500,
        instrument_key="NIFTY-22500-CE",
        provider_id=N.PROVIDER_DHAN,
    )
    cases.append(ok(
        "option_strike_context_only_not_live_present",
        opt_strike_only["present"] is False
        and opt_strike_only["metadata_present"] is True
        and opt_strike_only["quote_present"] is False
        and opt_strike_only["book_present"] is False,
        opt_strike_only,
    ))

    opt_good = O.build_live_option_surface(
        side=N.SIDE_CALL,
        live_source={
            "instrument_key": "NIFTY-22500-CE",
            "ltp": 100.0,
            "best_bid": 99.95,
            "best_ask": 100.05,
            "bid_qty": 100,
            "ask_qty": 100,
            "ts_event_ns": 1,
        },
        provider_id=N.PROVIDER_DHAN,
    )
    cases.append(ok(
        "option_live_quote_present_passes",
        opt_good["present"] is True
        and opt_good["live_present"] is True
        and opt_good["fresh"] is True,
        opt_good,
    ))

    trad_missing = T.build_classic_option_tradability_surface(
        option_surface={"selected_features": {}},
        branch_id=N.BRANCH_CALL,
        regime="NORMAL",
        runtime_mode="NORMAL",
        selection_label="active_atm",
    )
    cases.append(ok(
        "tradability_missing_values_fail_diagnostically",
        trad_missing["present"] is False
        and trad_missing["entry_pass"] is False
        and trad_missing["blocked_reason"] == "not_present"
        and trad_missing["spread_ratio"] is None
        and trad_missing["depth_total"] is None
        and trad_missing["response_efficiency"] is None
        and trad_missing["spread_pass"] is False
        and trad_missing["depth_pass"] is False
        and trad_missing["response_pass"] is False,
        trad_missing,
    ))

    weak_ctx = {
        "present": True,
        "context_status": N.PROVIDER_STATUS_HEALTHY,
        "age_ms": 0,
    }
    dhan_futures = {
        "present": True,
        "live_present": True,
        "fresh": True,
        "instrument_key": "NIFTY-FUT",
        "ltp": 22500,
        "ts_event_ns": 1,
        "age_ms": 0,
        "stale": False,
    }
    dhan_call = {
        "present": True,
        "selected_features": {
            "present": True,
            "live_present": True,
            "ltp": 100,
            "instrument_key": "CE",
            "ts_event_ns": 1,
            "age_ms": 0,
            "stale": False,
        },
    }
    dhan_put = {
        "present": True,
        "selected_features": {
            "present": True,
            "live_present": True,
            "ltp": 100,
            "instrument_key": "PE",
            "ts_event_ns": 1,
            "age_ms": 0,
            "stale": False,
        },
    }
    pr = {
        "futures_provider_status": N.PROVIDER_STATUS_HEALTHY,
        "selected_option_provider_status": N.PROVIDER_STATUS_HEALTHY,
        "option_context_provider_status": N.PROVIDER_STATUS_HEALTHY,
    }

    miso_weak = R.build_miso_runtime_mode_surface(
        provider_runtime=pr,
        dhan_futures_surface=dhan_futures,
        dhan_call_surface=dhan_call,
        dhan_put_surface=dhan_put,
        dhan_context=weak_ctx,
    )
    cases.append(ok(
        "regime_miso_healthy_but_weak_context_disabled",
        miso_weak["runtime_mode"] == "DISABLED"
        and miso_weak["miso_context_ready"] is False
        and miso_weak["blocked_reason"] == "context_incomplete",
        miso_weak,
    ))

    strong_ctx = {
        "present": True,
        "context_status": N.PROVIDER_STATUS_HEALTHY,
        "age_ms": 0,
        "atm_strike": 22500,
        "selected_call_instrument_key": "CE",
        "selected_put_instrument_key": "PE",
        "option_chain": [
            {"side": N.SIDE_CALL, "strike": 22500, "oi": 1000},
            {"side": N.SIDE_PUT, "strike": 22500, "oi": 1000},
        ],
    }
    miso_strong = R.build_miso_runtime_mode_surface(
        provider_runtime=pr,
        dhan_futures_surface=dhan_futures,
        dhan_call_surface=dhan_call,
        dhan_put_surface=dhan_put,
        dhan_context=strong_ctx,
    )
    cases.append(ok(
        "regime_miso_strong_context_base5_available",
        miso_strong["runtime_mode"] in {"BASE_5DEPTH", "DEPTH20_ENHANCED"}
        and miso_strong["miso_context_ready"] is True,
        miso_strong,
    ))

    ladder_no_atm = {
        "option_chain": [
            {"side": N.SIDE_CALL, "strike": 22500, "oi": 1000},
            {"side": N.SIDE_PUT, "strike": 22500, "oi": 1000},
            {"side": N.SIDE_CALL, "strike": 22600, "oi": 1200},
        ]
    }
    wall_no_atm = S.build_oi_wall_summary(dhan_context=ladder_no_atm)
    cases.append(ok(
        "strike_ladder_without_atm_not_oi_wall_ready",
        wall_no_atm["ladder_present"] is True
        and wall_no_atm["atm_reference_present"] is False
        and wall_no_atm["wall_computable"] is False
        and wall_no_atm["oi_wall_ready"] is False,
        wall_no_atm,
    ))

    miso_strike_no_atm = S.build_miso_strike_surface(
        dhan_context=ladder_no_atm,
        side=N.SIDE_CALL,
    )
    cases.append(ok(
        "miso_strike_without_atm_not_chain_context_ready",
        miso_strike_no_atm["chain_context_ready"] is False
        and miso_strike_no_atm["present"] is False,
        miso_strike_no_atm,
    ))

    payload = K.build_empty_family_features_payload(generated_at_ns=1)
    payload["snapshot"]["samples_seen"] = 1
    payload["provider_runtime"] = {
        "active_futures_provider_id": N.PROVIDER_ZERODHA,
        "active_selected_option_provider_id": N.PROVIDER_DHAN,
        "active_option_context_provider_id": N.PROVIDER_DHAN,
        "active_execution_provider_id": N.PROVIDER_ZERODHA,
        "fallback_execution_provider_id": N.PROVIDER_DHAN,
        "provider_runtime_mode": "NORMAL",
        "family_runtime_mode": N.FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        "futures_provider_status": N.PROVIDER_STATUS_UNAVAILABLE,
        "selected_option_provider_status": N.PROVIDER_STATUS_UNAVAILABLE,
        "option_context_provider_status": N.PROVIDER_STATUS_UNAVAILABLE,
        "execution_provider_status": N.PROVIDER_STATUS_UNAVAILABLE,
    }
    K.validate_publishable_family_features_payload(payload)
    cases.append(ok(
        "contracts_publishable_invalid_snapshot_is_publication_safe_not_entry_eligible",
        payload["snapshot"]["valid"] is False
        and payload["stage_flags"]["provider_ready_classic"] is False
        and payload["stage_flags"]["provider_ready_miso"] is False,
        {
            "snapshot_valid": payload["snapshot"]["valid"],
            "provider_ready_classic": payload["stage_flags"]["provider_ready_classic"],
            "provider_ready_miso": payload["stage_flags"]["provider_ready_miso"],
        },
    ))

    proof = {
        "proof_name": "feature_family_shared_core_guards",
        "status": "PASS",
        "ts_epoch": time.time(),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "provider_defaults_fail_closed": True,
            "live_metadata_distinction_proven": True,
            "tradability_missing_values_fail_diagnostically": True,
            "miso_context_strength_required": True,
            "oi_wall_readiness_required": True,
            "publishable_not_entry_eligible_documented": True,
        },
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
    print(f"proof_artifact={PROOF_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
