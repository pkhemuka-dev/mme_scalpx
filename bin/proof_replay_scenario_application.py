#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.scenarios import (  # noqa: E402
    REPLAY_REQUIRED_SCENARIOS,
    apply_replay_scenario_to_row,
    build_scenario_execution_assumption,
    scenario_risk_effects,
)
from app.mme_scalpx.replay.feature_adapter import build_replay_feature_payload  # noqa: E402
from app.mme_scalpx.replay.strategy_adapter import build_replay_strategy_decision_payload  # noqa: E402
from app.mme_scalpx.replay.risk_adapter import build_replay_risk_decision, validate_replay_risk_decision  # noqa: E402
from app.mme_scalpx.replay.execution_shadow import simulate_replay_execution_shadow, validate_replay_execution_shadow  # noqa: E402


def base_row() -> dict[str, object]:
    return {
        "event_ts_ns": 1_000_000_000,
        "sequence_id": 1,
        "data_valid": True,
        "fut_ltp": 22500.0,
        "fut_best_bid": 22499.5,
        "fut_best_ask": 22500.5,
        "fut_local_ts": 1_000_000_000,
        "opt_ltp": 100.0,
        "opt_best_bid": 99.5,
        "opt_best_ask": 100.5,
        "opt_bid_qty_1": 100,
        "opt_ask_qty_1": 100,
        "opt_local_ts": 1_000_000_000,
        "provider_ready_miso": True,
        "chain_context_fresh": True,
        "dhan_context_ready": True,
        "oi_context_fresh": True,
        "selected_security_id": "REPLAY-SEC",
        "selected_tradingsymbol": "NIFTY-REPLAY",
        "selected_expiry": "2026-05-07",
        "selected_strike": 22500,
        "selected_option_type": "CE",
        "nearest_call_wall": 22600,
        "nearest_put_wall": 22400,
        "oi_wall_strength": 1.25,
        "trend_confirmed": True,
        "pullback_detected": True,
        "resume_confirmed": True,
        "micro_trap_flag": True,
        "futures_impulse_ok": True,
        "shelf_confirmed": True,
        "breakout_triggered": True,
        "breakout_accepted": True,
        "shelf_high": 22520,
        "shelf_low": 22490,
        "compression_detected": True,
        "directional_breakout_triggered": True,
        "expansion_accepted": True,
        "retest_monitor_active": True,
        "hesitation_retest": True,
        "active_zone_valid": True,
        "active_zone": "ORB_LOW",
        "fake_break": True,
        "range_reentry": True,
        "flow_flip": True,
        "trap_event_id": "CALL|ORB_LOW|1000|2000",
        "burst_detected": True,
        "burst_event_id": "CALL|REPLAY-SEC|1000",
        "aggression_ok": True,
        "tape_speed_ok": True,
        "imbalance_persistence_ok": True,
        "queue_reload_veto": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_scenario_application.json")
    args = parser.parse_args()

    scenario_results = {}
    all_application_ok = True

    for scenario_id in REPLAY_REQUIRED_SCENARIOS:
        run_id = f"replay_scenario_{scenario_id}"
        row = apply_replay_scenario_to_row(base_row(), scenario_id)

        feature_result = build_replay_feature_payload(run_id=run_id, row=row)
        strategy_result = build_replay_strategy_decision_payload(run_id=run_id, feature_payload=feature_result.payload)

        risk_effects = scenario_risk_effects(scenario_id)
        risk_decision = build_replay_risk_decision(
            run_id=run_id,
            strategy_decision=strategy_result.decision_payload,
            force_veto_reasons=risk_effects.get("force_veto_reasons"),
        )
        risk_validation = validate_replay_risk_decision(risk_decision)

        assumption = build_scenario_execution_assumption(scenario_id)
        execution_shadow = simulate_replay_execution_shadow(
            run_id=run_id,
            strategy_decision=strategy_result.decision_payload,
            risk_decision=risk_decision,
            assumption_profile=assumption,
        )
        execution_validation = validate_replay_execution_shadow(execution_shadow)

        explicit_assumption_ok = (
            row.get("explicit_assumption") is True
            and assumption.get("explicit_assumption") is True
        )
        scenario_tag_ok = scenario_id in row.get("scenario_tags", ())
        no_live_ok = (
            row.get("paper_armed_approved") is False
            and row.get("live_trading_approved") is False
            and row.get("production_doctrine_changed") is False
            and risk_decision.get("paper_armed_approved") is False
            and risk_decision.get("live_trading_approved") is False
            and risk_decision.get("execution_arming_created") is False
            and execution_shadow.get("real_order_sent") is False
            and execution_shadow.get("broker_calls_executed") is False
            and execution_shadow.get("live_redis_writes_executed") is False
            and execution_shadow.get("paper_armed_approved") is False
            and execution_shadow.get("live_trading_approved") is False
            and execution_shadow.get("execution_arming_created") is False
            and execution_shadow.get("production_doctrine_changed") is False
        )

        scenario_ok = bool(
            explicit_assumption_ok
            and scenario_tag_ok
            and risk_validation.get("ok") is True
            and execution_validation.get("ok") is True
            and no_live_ok
        )

        all_application_ok = all_application_ok and scenario_ok

        scenario_results[scenario_id] = {
            "ok": scenario_ok,
            "explicit_assumption_ok": explicit_assumption_ok,
            "scenario_tag_ok": scenario_tag_ok,
            "risk_validation_ok": risk_validation.get("ok"),
            "execution_validation_ok": execution_validation.get("ok"),
            "no_live_ok": no_live_ok,
            "risk_entry_vetoed": risk_decision.get("entry_vetoed"),
            "research_trade_allowed": risk_decision.get("research_trade_allowed"),
            "fill_policy": execution_shadow.get("fill_policy"),
            "fill_status": execution_shadow.get("fill_status"),
            "filled_qty": execution_shadow.get("filled_qty"),
            "net_pnl": execution_shadow.get("shadow_pnl_summary", {}).get("net_pnl"),
        }

    forced_veto_ok = scenario_results["forced_risk_veto"]["risk_entry_vetoed"] is True
    session_close_ok = scenario_results["session_close"]["risk_entry_vetoed"] is True
    forced_flatten_ok = scenario_results["forced_flatten"]["risk_entry_vetoed"] is True
    partial_fill_ok = scenario_results["partial_fill"]["fill_status"] in {"PARTIAL_FILLED", "RISK_VETOED"}
    no_fill_ok = scenario_results["no_fill"]["fill_status"] in {"NO_FILL", "RISK_VETOED"}
    rejected_ok = scenario_results["rejected"]["fill_status"] in {"REJECTED", "RISK_VETOED"}
    high_slippage_ok = scenario_results["high_slippage"]["fill_policy"] == "FULL_FILL"
    liquidity_shock_ok = scenario_results["liquidity_shock"]["fill_policy"] == "PARTIAL_FILL"

    application_ok = bool(
        all_application_ok
        and forced_veto_ok
        and session_close_ok
        and forced_flatten_ok
        and partial_fill_ok
        and no_fill_ok
        and rejected_ok
        and high_slippage_ok
        and liquidity_shock_ok
    )

    proof = {
        "schema_version": "proof_replay_scenario_application_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_application_ok": application_ok,
        "all_application_ok": all_application_ok,
        "scenario_count": len(scenario_results),
        "required_scenario_count": len(REPLAY_REQUIRED_SCENARIOS),
        "forced_veto_ok": forced_veto_ok,
        "session_close_ok": session_close_ok,
        "forced_flatten_ok": forced_flatten_ok,
        "partial_fill_ok": partial_fill_ok,
        "no_fill_ok": no_fill_ok,
        "rejected_ok": rejected_ok,
        "high_slippage_ok": high_slippage_ok,
        "liquidity_shock_ok": liquidity_shock_ok,
        "scenario_results": scenario_results,
        "scenario_profile_shape": "PROVEN_BY_27J",
        "scenario_application_shape": "PROVEN_BY_27J",
        "full_replay_scenario_outcome_parity": "NOT_PROVEN_IN_27J",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if application_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "scenario_application_ok": application_ok,
        "scenario_count": proof["scenario_count"],
        "forced_veto_ok": forced_veto_ok,
        "partial_fill_ok": partial_fill_ok,
        "no_fill_ok": no_fill_ok,
        "rejected_ok": rejected_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if application_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
