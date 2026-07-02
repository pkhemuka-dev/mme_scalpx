#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import py_compile
import subprocess
import time

from app.mme_scalpx.replay import miv_research_evaluator as E
from app.mme_scalpx.services.strategy_family import miv_r_contract as MIV

OUT_DIR = pathlib.Path("run/audits/LANE-MIV-R2C_NEUTRAL_LABEL_ROUTE_PROOF_NO_PATCH_NO_REPLAY_NO_ORDER_prove_neutral_active_label_emits_as_label_only_and_never_routes_to_risk_execution_order_intent_20260611_232522_neutral_artifacts")


def git_status() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], text=True, stderr=subprocess.STDOUT)
    except Exception as exc:
        return f"ERROR: {exc}"


def main() -> None:
    py_compile.compile("app/mme_scalpx/replay/miv_research_evaluator.py", doraise=True)
    py_compile.compile("app/mme_scalpx/services/strategy_family/miv_r_contract.py", doraise=True)

    # Unknown option type + active tradable tape for enough rows to cross neutral activity threshold.
    neutral_rows = [
        {
            "event_ns": 1,
            "event_ts": "2026-06-11T09:21:00+05:30",
            "futures_ltp": 23000.0,
            "selected_option_ltp": 100.0,
            "selected_bid": 99.5,
            "selected_ask": 100.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
        {
            "event_ns": 2,
            "event_ts": "2026-06-11T09:21:01+05:30",
            "futures_ltp": 23000.5,
            "selected_option_ltp": 104.0,
            "selected_bid": 103.5,
            "selected_ask": 104.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
        {
            "event_ns": 3,
            "event_ts": "2026-06-11T09:21:02+05:30",
            "futures_ltp": 23000.9,
            "selected_option_ltp": 108.0,
            "selected_bid": 107.5,
            "selected_ask": 108.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
        {
            "event_ns": 4,
            "event_ts": "2026-06-11T09:21:03+05:30",
            "futures_ltp": 23001.2,
            "selected_option_ltp": 112.0,
            "selected_bid": 111.5,
            "selected_ask": 112.5,
            "selected_depth_bid": 1500,
            "selected_depth_ask": 1500,
            "selected_symbol": "NIFTY_TEST_UNKNOWN",
        },
    ]

    result = E.evaluate_miv_zerodha_lite_rows(
        neutral_rows,
        run_id="miv_r2c_neutral_label_route",
        dataset_id="synthetic_neutral_no_replay",
        emit_neutral_labels=True,
    )

    paths = E.write_miv_research_artifacts(result, OUT_DIR)

    candidates = list(result.get("candidates", []))
    neutral_candidates = [c for c in candidates if c.get("candidate_type") == MIV.MIV_NEUTRAL_ACTIVE_LABEL]
    bad_routes = [
        c for c in neutral_candidates
        if c.get("route_to_risk_shadow")
        or c.get("route_to_execution_shadow")
        or c.get("route_to_order_intent_ledger")
        or c.get("trade_shadow_eligible")
        or not c.get("label_only")
    ]

    checks = {
        "module_compiles": True,
        "neutral_candidate_count_positive": len(neutral_candidates) > 0,
        "all_neutral_candidates_contract_valid": all(c.get("contract_validation_ok") is True for c in neutral_candidates),
        "all_neutral_candidates_label_only": all(c.get("label_only") is True for c in neutral_candidates),
        "all_neutral_candidates_trade_shadow_false": all(c.get("trade_shadow_eligible") is False for c in neutral_candidates),
        "all_neutral_candidates_risk_route_false": all(c.get("route_to_risk_shadow") is False for c in neutral_candidates),
        "all_neutral_candidates_execution_route_false": all(c.get("route_to_execution_shadow") is False for c in neutral_candidates),
        "all_neutral_candidates_order_intent_route_false": all(c.get("route_to_order_intent_ledger") is False for c in neutral_candidates),
        "all_neutral_candidates_order_allowed_false": all(c.get("order_allowed") is False for c in neutral_candidates),
        "all_neutral_candidates_broker_send_false": all(c.get("broker_send_enabled") is False for c in neutral_candidates),
        "all_neutral_candidates_real_order_false": all(c.get("real_order_sent") is False for c in neutral_candidates),
        "no_bad_neutral_routes": len(bad_routes) == 0,
        "all_artifacts_exist": all(pathlib.Path(p).exists() for p in paths.values()),
    }

    classification = (
        "PASS_MIV_R2C_NEUTRAL_LABEL_ROUTE_PROOF_NO_PATCH_NO_REPLAY_NO_ORDER"
        if all(checks.values())
        else "REVIEW_MIV_R2C_NEUTRAL_LABEL_ROUTE_NOT_PROVEN"
    )

    print(json.dumps({
        "batch": "LANE-MIV-R2C_NEUTRAL_LABEL_ROUTE_PROOF_NO_PATCH_NO_REPLAY_NO_ORDER",
        "classification": classification,
        "created_at_epoch": time.time(),
        "checks": checks,
        "candidate_count": result.get("candidate_count"),
        "neutral_candidate_count": len(neutral_candidates),
        "trade_candidate_count": result.get("trade_candidate_count"),
        "neutral_label_count": result.get("neutral_label_count"),
        "first_neutral_candidate": neutral_candidates[0] if neutral_candidates else None,
        "bad_routes": bad_routes,
        "artifact_paths": paths,
        "safety": {
            "source_patch": False,
            "replay_execution": False,
            "broker_order": False,
            "risk_service_start": False,
            "execution_service_start": False,
            "redis_delete": False,
            "lock_delete": False,
            "production_registry_change": False,
            "paper_live_enabled": False,
        },
        "git_status_short": git_status(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
