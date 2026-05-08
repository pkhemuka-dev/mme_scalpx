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
from app.mme_scalpx.replay.risk_adapter import (  # noqa: E402
    build_replay_risk_decision,
    publish_replay_risk_shadow,
    replay_risk_adapter_contract_summary,
    validate_replay_risk_decision,
)
from app.mme_scalpx.replay.execution_shadow import (  # noqa: E402
    REPLAY_SHADOW_FILL_POLICIES,
    publish_replay_execution_shadow,
    replay_execution_shadow_contract_summary,
    replay_shadow_assumption_profile,
    simulate_replay_execution_shadow,
    validate_replay_execution_shadow,
)
from app.mme_scalpx.replay.transport import LocalReplayTransport


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
    parser.add_argument("--out", default="run/proofs/proof_replay_risk_execution_shadow.json")
    args = parser.parse_args()

    run_id = "replay_risk_execution_shadow_smoke"
    feature_result = build_replay_feature_payload(run_id=run_id, row=sample_row())
    strategy_result = build_replay_strategy_decision_payload(run_id=run_id, feature_payload=feature_result.payload)

    risk_pass = build_replay_risk_decision(
        run_id=run_id,
        strategy_decision=strategy_result.decision_payload,
        max_loss_points=12.0,
        max_slippage_points=2.0,
    )
    risk_veto = build_replay_risk_decision(
        run_id=run_id,
        strategy_decision=strategy_result.decision_payload,
        max_loss_points=12.0,
        max_slippage_points=2.0,
        force_veto_reasons=("forced_replay_risk_veto_smoke",),
    )

    risk_pass_validation = validate_replay_risk_decision(risk_pass)
    risk_veto_validation = validate_replay_risk_decision(risk_veto)

    profiles = {
        policy: replay_shadow_assumption_profile(
            fill_policy=policy,
            requested_qty=75,
            partial_fill_ratio=0.4,
            entry_reference_price=100.0,
            exit_reference_price=104.0,
            slippage_points=0.5,
            transaction_cost_points=0.25,
            reject_reason="replay_assumption_reject",
        )
        for policy in REPLAY_SHADOW_FILL_POLICIES
    }

    execution_results = {
        policy: simulate_replay_execution_shadow(
            run_id=run_id,
            strategy_decision=strategy_result.decision_payload,
            risk_decision=risk_pass,
            assumption_profile=profile,
        )
        for policy, profile in profiles.items()
    }

    veto_execution = simulate_replay_execution_shadow(
        run_id=run_id,
        strategy_decision=strategy_result.decision_payload,
        risk_decision=risk_veto,
        assumption_profile=profiles["FULL_FILL"],
    )

    execution_validations = {
        policy: validate_replay_execution_shadow(payload)
        for policy, payload in execution_results.items()
    }
    veto_execution_validation = validate_replay_execution_shadow(veto_execution)

    transport = LocalReplayTransport(run_id=run_id)
    risk_state = publish_replay_risk_shadow(
        transport,
        run_id=run_id,
        risk_decision=risk_pass,
        updated_ts_ns=4_000_000_000,
    )
    execution_state = publish_replay_execution_shadow(
        transport,
        run_id=run_id,
        execution_shadow=execution_results["FULL_FILL"],
        updated_ts_ns=4_000_000_001,
    )
    snapshot = transport.snapshot()

    fill_policy_coverage_ok = set(execution_results.keys()) == set(REPLAY_SHADOW_FILL_POLICIES)
    execution_validations_ok = all(v.get("ok") is True for v in execution_validations.values())
    no_real_order_ok = (
        all(payload.get("real_order_sent") is False for payload in execution_results.values())
        and all(payload.get("broker_calls_executed") is False for payload in execution_results.values())
        and all(payload.get("live_redis_writes_executed") is False for payload in execution_results.values())
        and veto_execution.get("real_order_sent") is False
        and veto_execution.get("broker_calls_executed") is False
    )
    risk_shape_ok = (
        risk_pass_validation.get("ok") is True
        and risk_veto_validation.get("ok") is True
        and risk_pass.get("research_trade_allowed") is True
        and risk_pass.get("entry_vetoed") is False
        and risk_veto.get("entry_vetoed") is True
    )
    shadow_state_ok = (
        risk_state.get("surface") == "risk_shadow"
        and execution_state.get("surface") == "execution_shadow"
        and snapshot.get("state_count") == 2
    )

    proof_ok = bool(
        risk_shape_ok
        and fill_policy_coverage_ok
        and execution_validations_ok
        and veto_execution_validation.get("ok") is True
        and no_real_order_ok
        and shadow_state_ok
    )

    proof = {
        "schema_version": "proof_replay_risk_execution_shadow_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "risk_execution_shadow_ok": proof_ok,
        "risk_shape_ok": risk_shape_ok,
        "risk_pass_validation": risk_pass_validation,
        "risk_veto_validation": risk_veto_validation,
        "fill_policy_coverage_ok": fill_policy_coverage_ok,
        "execution_validations_ok": execution_validations_ok,
        "veto_execution_validation_ok": veto_execution_validation.get("ok"),
        "no_real_order_ok": no_real_order_ok,
        "shadow_state_ok": shadow_state_ok,
        "risk_pass": risk_pass,
        "risk_veto": risk_veto,
        "execution_results": execution_results,
        "veto_execution": veto_execution,
        "execution_validations": execution_validations,
        "risk_state": risk_state,
        "execution_state": execution_state,
        "transport_snapshot": snapshot,
        "risk_contract_summary": replay_risk_adapter_contract_summary(),
        "execution_contract_summary": replay_execution_shadow_contract_summary(),
        "risk_shape_parity": "PROVEN_BY_27I",
        "execution_shadow_shape": "PROVEN_BY_27I",
        "real_execution_parity": "NOT_PROVEN_IN_27I",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if proof_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "risk_execution_shadow_ok": proof_ok,
        "risk_shape_ok": risk_shape_ok,
        "fill_policy_coverage_ok": fill_policy_coverage_ok,
        "execution_validations_ok": execution_validations_ok,
        "no_real_order_ok": no_real_order_ok,
        "shadow_state_ok": shadow_state_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
