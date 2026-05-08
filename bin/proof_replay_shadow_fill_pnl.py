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

from app.mme_scalpx.replay.feature_adapter import build_replay_feature_payload  # noqa: E402
from app.mme_scalpx.replay.strategy_adapter import build_replay_strategy_decision_payload  # noqa: E402
from app.mme_scalpx.replay.risk_adapter import build_replay_risk_decision  # noqa: E402
from app.mme_scalpx.replay.execution_shadow import (  # noqa: E402
    REPLAY_SHADOW_FILL_POLICIES,
    replay_shadow_assumption_profile,
    simulate_replay_execution_shadow,
)


def sample_row() -> dict[str, object]:
    return {
        "provider_ready_miso": True,
        "chain_context_fresh": True,
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
    parser.add_argument("--out", default="run/proofs/proof_replay_shadow_fill_pnl.json")
    args = parser.parse_args()

    run_id = "replay_shadow_fill_pnl_smoke"
    feature_result = build_replay_feature_payload(run_id=run_id, row=sample_row())
    strategy_result = build_replay_strategy_decision_payload(run_id=run_id, feature_payload=feature_result.payload)
    risk_decision = build_replay_risk_decision(run_id=run_id, strategy_decision=strategy_result.decision_payload)

    scenarios = {
        "FULL_FILL": {"requested_qty": 75, "partial_fill_ratio": 0.4, "entry_reference_price": 100.0, "exit_reference_price": 104.0, "slippage_points": 0.5, "transaction_cost_points": 0.25},
        "PARTIAL_FILL": {"requested_qty": 75, "partial_fill_ratio": 0.4, "entry_reference_price": 100.0, "exit_reference_price": 104.0, "slippage_points": 0.5, "transaction_cost_points": 0.25},
        "NO_FILL": {"requested_qty": 75, "partial_fill_ratio": 0.4, "entry_reference_price": 100.0, "exit_reference_price": 104.0, "slippage_points": 0.5, "transaction_cost_points": 0.25},
        "REJECTED": {"requested_qty": 75, "partial_fill_ratio": 0.4, "entry_reference_price": 100.0, "exit_reference_price": 104.0, "slippage_points": 0.5, "transaction_cost_points": 0.25},
    }

    results = {}
    for policy, kwargs in scenarios.items():
        profile = replay_shadow_assumption_profile(fill_policy=policy, **kwargs)
        results[policy] = simulate_replay_execution_shadow(
            run_id=run_id,
            strategy_decision=strategy_result.decision_payload,
            risk_decision=risk_decision,
            assumption_profile=profile,
        )

    full = results["FULL_FILL"]
    partial = results["PARTIAL_FILL"]
    no_fill = results["NO_FILL"]
    rejected = results["REJECTED"]

    full_fill_math_ok = (
        full["fill_status"] == "FILLED"
        and full["filled_qty"] == 75
        and full["shadow_pnl_summary"]["net_pnl"] == ((104.0 - 0.5) - (100.0 + 0.5) - 0.25) * 75
    )
    partial_fill_math_ok = (
        partial["fill_status"] == "PARTIAL_FILLED"
        and partial["filled_qty"] == 30
        and partial["shadow_pnl_summary"]["net_pnl"] == ((104.0 - 0.5) - (100.0 + 0.5) - 0.25) * 30
    )
    no_fill_math_ok = (
        no_fill["fill_status"] == "NO_FILL"
        and no_fill["filled_qty"] == 0
        and no_fill["shadow_pnl_summary"]["net_pnl"] == 0.0
    )
    rejected_math_ok = (
        rejected["fill_status"] == "REJECTED"
        and rejected["filled_qty"] == 0
        and rejected["shadow_pnl_summary"]["net_pnl"] == 0.0
    )

    real_safety_ok = all(
        payload.get("real_order_sent") is False
        and payload.get("broker_calls_executed") is False
        and payload.get("live_redis_writes_executed") is False
        and payload.get("paper_armed_approved") is False
        and payload.get("live_trading_approved") is False
        and payload.get("execution_arming_created") is False
        and payload.get("production_doctrine_changed") is False
        for payload in results.values()
    )

    pnl_shadow_ok = bool(
        set(results) == set(REPLAY_SHADOW_FILL_POLICIES)
        and full_fill_math_ok
        and partial_fill_math_ok
        and no_fill_math_ok
        and rejected_math_ok
        and real_safety_ok
    )

    proof = {
        "schema_version": "proof_replay_shadow_fill_pnl_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pnl_shadow_ok": pnl_shadow_ok,
        "fill_policy_coverage_ok": set(results) == set(REPLAY_SHADOW_FILL_POLICIES),
        "full_fill_math_ok": full_fill_math_ok,
        "partial_fill_math_ok": partial_fill_math_ok,
        "no_fill_math_ok": no_fill_math_ok,
        "rejected_math_ok": rejected_math_ok,
        "real_safety_ok": real_safety_ok,
        "results": results,
        "pnl_shadow_math": "PROVEN_BY_27I",
        "real_execution_parity": "NOT_PROVEN_IN_27I",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if pnl_shadow_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "pnl_shadow_ok": pnl_shadow_ok,
        "fill_policy_coverage_ok": proof["fill_policy_coverage_ok"],
        "full_fill_math_ok": full_fill_math_ok,
        "partial_fill_math_ok": partial_fill_math_ok,
        "no_fill_math_ok": no_fill_math_ok,
        "rejected_math_ok": rejected_math_ok,
        "real_safety_ok": real_safety_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if pnl_shadow_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
