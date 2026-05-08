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
from app.mme_scalpx.replay.strategy_adapter import (  # noqa: E402
    arbitrate_replay_strategy_candidates,
    build_replay_strategy_candidates,
    build_replay_strategy_decision_payload,
    publish_replay_strategy_decision,
    validate_replay_strategy_arbitration,
    validate_replay_strategy_candidates,
)
from app.mme_scalpx.replay.transport import LocalReplayTransport, assert_live_shape_event  # noqa: E402


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
    parser.add_argument("--out", default="run/proofs/proof_replay_family_arbitration.json")
    args = parser.parse_args()

    run_id = "replay_strategy_arbitration_smoke"
    feature_result = build_replay_feature_payload(run_id=run_id, row=sample_row())
    feature_payload = feature_result.payload

    candidates = build_replay_strategy_candidates(run_id=run_id, feature_payload=feature_payload)
    candidate_validation = validate_replay_strategy_candidates(candidates)

    arbitration = arbitrate_replay_strategy_candidates(run_id=run_id, candidates=candidates)
    arbitration_validation = validate_replay_strategy_arbitration(arbitration)

    decision_result = build_replay_strategy_decision_payload(run_id=run_id, feature_payload=feature_payload)
    decision_payload = decision_result.decision_payload

    transport = LocalReplayTransport(run_id=run_id)
    event = publish_replay_strategy_decision(
        transport,
        run_id=run_id,
        feature_payload=feature_payload,
        event_ts_ns=3_000_000_000,
        sequence_id=1,
    )
    assert_live_shape_event(event)
    snapshot = transport.snapshot()

    final_action_hold_ok = (
        arbitration.get("final_action") == "HOLD_REPORT_ONLY"
        and decision_payload.get("final_action") == "HOLD_REPORT_ONLY"
        and event.get("payload", {}).get("final_action") == "HOLD_REPORT_ONLY"
    )

    no_order_ok = (
        arbitration.get("order_allowed") is False
        and arbitration.get("real_order_intent_generated") is False
        and decision_payload.get("order_allowed") is False
        and decision_payload.get("real_order_intent_generated") is False
        and event.get("payload", {}).get("order_allowed") is False
        and event.get("payload", {}).get("real_order_intent_generated") is False
    )

    no_approval_ok = (
        arbitration.get("paper_armed_approved") is False
        and arbitration.get("live_trading_approved") is False
        and arbitration.get("execution_arming_created") is False
        and arbitration.get("production_doctrine_changed") is False
        and decision_payload.get("paper_armed_approved") is False
        and decision_payload.get("live_trading_approved") is False
        and decision_payload.get("execution_arming_created") is False
        and decision_payload.get("production_doctrine_changed") is False
        and event.get("paper_armed_approved") is False
        and event.get("live_trading_approved") is False
        and event.get("production_doctrine_changed") is False
    )

    transport_ok = (
        event.get("surface") == "strategy_decision"
        and event.get("replay_key", "").startswith("replay:")
        and snapshot.get("event_count") == 1
    )

    arbitration_ok = bool(
        candidate_validation.get("ok") is True
        and arbitration_validation.get("ok") is True
        and arbitration.get("candidate_count") == 10
        and final_action_hold_ok
        and no_order_ok
        and no_approval_ok
        and transport_ok
    )

    proof = {
        "schema_version": "proof_replay_family_arbitration_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "family_arbitration_ok": arbitration_ok,
        "candidate_validation_ok": candidate_validation.get("ok"),
        "arbitration_validation_ok": arbitration_validation.get("ok"),
        "candidate_count": arbitration.get("candidate_count"),
        "eligible_candidate_count": arbitration.get("eligible_candidate_count"),
        "winner_present": arbitration.get("winner") is not None,
        "winning_family": arbitration.get("winning_family"),
        "winning_side": arbitration.get("winning_side"),
        "final_action_hold_ok": final_action_hold_ok,
        "no_order_ok": no_order_ok,
        "no_approval_ok": no_approval_ok,
        "transport_ok": transport_ok,
        "candidate_validation": candidate_validation,
        "arbitration_validation": arbitration_validation,
        "arbitration": arbitration,
        "decision_payload": decision_payload,
        "sample_event": event,
        "snapshot": snapshot,
        "full_live_strategy_decision_parity": "NOT_PROVEN_IN_27H",
        "safe_decision_shape_parity": "PROVEN_BY_27H",
        "arbitration_surface": "PROVEN_BY_27H",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if arbitration_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "family_arbitration_ok": arbitration_ok,
        "candidate_count": proof["candidate_count"],
        "winner_present": proof["winner_present"],
        "final_action_hold_ok": final_action_hold_ok,
        "no_order_ok": no_order_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if arbitration_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
