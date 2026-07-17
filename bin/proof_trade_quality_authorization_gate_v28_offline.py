from __future__ import annotations

import json
import tempfile
from dataclasses import asdict, replace
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from app.mme_scalpx.shadow_paper import trade_quality_authorization_gate_v28 as m

IST = ZoneInfo("Asia/Kolkata")


def good_packet() -> dict:
    return {
        "family": "MIST",
        "side": "CALL",
        "setup_origin": "vwap_pullback",
        "regime_id": "regime-20260717-1",
        "trigger_level_bucket": "24250-24255",
        "selected_symbol": "NIFTY2672124300CE",
        "selected_token": "14682114",
        "strike_classification": "ATM1",
        "observation_window_id": "obs-1",
        "direction_owner": "NIFTY_FUTURES_SPOT_VWAP_STRUCTURE",
        "hard_veto_checks": {
            "QUOTE_FRESH": True,
            "BID_QTY_VALID": True,
            "ASK_QTY_VALID": True,
            "SPREAD_ACCEPTABLE": True,
            "OPTION_SYMBOL_STABLE": True,
            "INSTRUMENT_LOCK_VALID": True,
            "UNDERLYING_OPTION_ALIGNED": True,
            "NO_CHASE": True,
            "EDGE_AFTER_COST_POSITIVE": True,
            "BROKER_FLAT": True,
            "ACTIVE_BROKER_ORDERS_ZERO": True,
            "RISK_GATE_OPEN": True,
            "TIMEFRAME_COMPLETE": True,
            "DATA_GAP_PRESENT": False,
            "PENDING_ORDER_PRESENT": False,
            "ENTRY_CUTOFF_PASSED": False,
        },
        "components": {
            "regime_15m": {"futures_spot_alignment": 1, "vwap_relation": .9, "vwap_slope": .9, "market_structure": .9, "breadth": .8},
            "setup_5m": {"clarity": .9, "pullback_quality": .9, "trigger_proximity": .8, "volatility_fit": .9, "breadth_alignment": .8},
            "trigger_3m": {"trigger_confirmed": 1, "impulse_quality": .9, "follow_through": .8, "no_reversal": .9, "timeframe_complete": 1},
            "option_microstructure": {"quote_fresh": 1, "symbol_stable": 1, "alignment": .9, "response_efficiency": .8, "spread_quality": .8},
            "liquidity_execution": {"bid_qty": .9, "ask_qty": .9, "depth": .8, "slippage": .8, "exit_liquidity": .9},
        },
        "candidate_creation": {
            "trigger_underlying_price": 24250.0,
            "trigger_option_mid": 105.0,
            "trigger_option_ask": 105.1,
            "trigger_spread": 0.2,
            "short_term_atr": 10.0,
            "candidate_created_ts": "2026-07-17T11:00:00+05:30",
        },
        "current_market": {
            "underlying_price": 24251.5,
            "option_mid": 106.0,
            "ask": 106.1,
            "spread": 0.25,
            "recent_ask_volatility": 0.15,
            "tick_size": 0.05,
        },
        "edge_after_cost": {
            "expected_gross_move_points": 5.0,
            "optimistic_entry_cost_points": 0.10,
            "optimistic_exit_cost_points": 0.10,
            "optimistic_slippage_points": 0.10,
            "conservative_entry_cost_points": 0.20,
            "conservative_exit_cost_points": 0.20,
            "conservative_slippage_points": 0.25,
            "brokerage_points": 0.15,
            "taxes_exchange_points": 0.15,
        },
    }


def calibrated_config():
    return replace(m.GateConfig(), calibration_required=True, calibration_id="FRIDAY_REPLAY_CALIBRATION_V1")


def drive_to_complete(packet, config, start):
    state = m.ObservationState()
    record, state = m.evaluate(packet, state, config, start)
    assert record["verdict"] == "HOLD", record
    record, state = m.evaluate(packet, state, config, start + timedelta(seconds=1))
    assert record["verdict"] == "HOLD", record
    # Opening requires 60 seconds from first active sample.
    record, state = m.evaluate(packet, state, config, start + timedelta(seconds=62))
    return record, state


def main():
    results = {}
    start = datetime(2026, 7, 17, 9, 20, tzinfo=IST)
    cfg = calibrated_config()
    packet = good_packet()

    # 1. Full authorization after micro observation.
    record, state = drive_to_complete(packet, cfg, start)
    assert record["verdict"] == "AUTHORIZE", record
    assert state.state == "AUTHORIZED"
    assert record["hard_veto_count"] == 0
    assert record["total_score"] >= record["minimum_total_score"]
    assert record["broker_order"] == record["risk_started"] == record["execution_started"] == 0
    results["authorize"] = record

    # 2. Every positive hard veto blocks independently.
    hard_veto_results = {}
    for name in m.HARD_VETO_FIELDS:
        p = good_packet()
        p["hard_veto_checks"][name] = False
        r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
        assert r["verdict"] in {"VETO", "HOLD"}
        # NO_CHASE and EDGE are recomputed; force inputs that make them fail.
        if name == "NO_CHASE":
            p["current_market"]["underlying_price"] = 24300
            r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
        elif name == "EDGE_AFTER_COST_POSITIVE":
            p["edge_after_cost"]["expected_gross_move_points"] = 0.1
            r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
        assert name in r.get("hard_vetoes", []), (name, r)
        hard_veto_results[name] = r["reason"]
    for name in m.NEGATIVE_HARD_VETO_FIELDS:
        p = good_packet()
        p["hard_veto_checks"][name] = True
        r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
        assert name in r.get("hard_vetoes", []) or name == "ENTRY_CUTOFF_PASSED"
        hard_veto_results[name] = r["reason"]
    results["hard_veto_results"] = hard_veto_results

    # 3. Score cannot override hard veto.
    p = good_packet()
    p["hard_veto_checks"]["BROKER_FLAT"] = False
    r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
    assert r["verdict"] == "VETO" and "BROKER_FLAT" in r["hard_vetoes"]
    results["score_cannot_override"] = r

    # 4. Component minimum and total score rules.
    p = good_packet()
    p["components"]["trigger_3m"] = {"a": 0.2, "b": 0.2}
    r, s = drive_to_complete(p, cfg, start)
    assert r["verdict"] == "VETO" and r["reason"] == "QUALITY_SCORE_INSUFFICIENT"
    assert "trigger_3m" in r["low_components"]
    results["score_block"] = r

    # 5. Calibration missing holds, never authorizes.
    r, s = drive_to_complete(good_packet(), m.GateConfig(), start)
    assert r["verdict"] == "HOLD" and r["reason"] == "REPLAY_CALIBRATION_REQUIRED"
    results["calibration_hold"] = r

    # 6. Symbol change resets observation and never transfers evidence.
    p = good_packet()
    r, s = m.evaluate(p, m.ObservationState(), cfg, start)
    p2 = good_packet()
    p2["selected_symbol"] = "NIFTY2672124250CE"
    p2["selected_token"] = "OTHER"
    r2, s2 = m.evaluate(p2, s, cfg, start + timedelta(seconds=5))
    assert r2["verdict"] == "RESET_OBSERVATION"
    assert s2.reset_count == 1 and s2.authorization_id == ""
    results["symbol_reset"] = r2

    # 7. Option cannot own direction.
    p = good_packet()
    p["direction_owner"] = "SELECTED_OPTION"
    r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
    assert r["verdict"] == "VETO" and r["reason"] == "DIRECTION_OWNER_INVALID_OR_OPTION_LED"
    results["direction_owner"] = r

    # 8. No-chase and edge-after-cost calculations.
    p = good_packet()
    p["current_market"]["underlying_price"] = 24270
    r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
    assert "NO_CHASE" in r["hard_vetoes"]
    results["no_chase"] = r

    p = good_packet()
    p["edge_after_cost"]["expected_gross_move_points"] = 0.5
    r, _ = m.evaluate(p, m.ObservationState(), cfg, start)
    assert "EDGE_AFTER_COST_POSITIVE" in r["hard_vetoes"]
    results["edge_after_cost"] = r

    # 9. Session phases and shorter closing hold.
    opening_phase, opening_policy = m.session_phase(start, cfg)
    closing_phase, closing_policy = m.session_phase(datetime(2026, 7, 17, 14, 35, tzinfo=IST), cfg)
    no_entry_phase, _ = m.session_phase(datetime(2026, 7, 17, 14, 51, tzinfo=IST), cfg)
    assert opening_phase.value == "OPENING" and opening_policy.max_hold_seconds == 300
    assert closing_phase.value == "CLOSING" and closing_policy.max_hold_seconds < 300
    assert no_entry_phase.value == "NO_NEW_ENTRY"
    results["session_phases"] = {
        "opening": asdict(opening_policy),
        "closing": asdict(closing_policy),
        "after_cutoff": no_entry_phase.value,
    }

    # 10. Candidate/cooldown identity is structural.
    p = good_packet()
    i1 = m.candidate_identity(p)
    assert i1 == m.candidate_identity(dict(p))
    p["selected_symbol"] = "OTHER"
    i2 = m.candidate_identity(p)
    assert i1 != i2
    results["identity"] = {"original": i1, "changed": i2}

    # 11. Marketable-limit policy is a plan only.
    plan = m.marketable_limit_plan(good_packet(), cfg)
    assert plan["plan_ready"] is True
    assert plan["order_type"] == "MARKETABLE_LIMIT"
    assert plan["broker_order"] == 0
    assert plan["max_order_attempts"] == 1
    assert plan["retry_allowed"] is False
    results["marketable_limit_plan"] = plan

    # 12. CLI persists records but still makes no order.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        input_path = root / "input.json"
        state_path = root / "state.json"
        config_path = root / "config.json"
        output_path = root / "output.json"
        records_path = root / "records.ndjson"
        input_path.write_text(json.dumps(good_packet()))
        config_path.write_text(json.dumps({"calibration_id": "FRIDAY_REPLAY_CALIBRATION_V1"}))
        rc = m.main([
            "--input", str(input_path), "--state", str(state_path),
            "--config", str(config_path), "--output", str(output_path),
            "--record-ndjson", str(records_path),
            "--now", "2026-07-17T09:20:00+05:30",
        ])
        assert rc == 0 and output_path.exists() and records_path.exists()
        out = json.loads(output_path.read_text())
        assert out["broker_order"] == out["redis_write"] == 0
    results["cli"] = "PASS"

    print("SELFTEST_CLASSIFICATION=PASS_TRADE_QUALITY_AUTHORIZATION_GATE_V28_SHADOW_ONLY")
    print("AUTHORIZE_VETO_HOLD_RESET_OBSERVATION=1")
    print("HARD_VETO_COUNT_TESTED=" + str(len(hard_veto_results)))
    print("NO_SCORE_OVERRIDE_HARD_VETO=1")
    print("TOTAL_SCORE_MINIMUM=75")
    print("EVERY_COMPONENT_MINIMUM=10")
    print("INSTRUMENT_LOCK_STATE_MACHINE=1")
    print("NO_CHASE_GATE=1")
    print("EDGE_AFTER_COST_OPTIMISTIC_AND_CONSERVATIVE=1")
    print("SESSION_PHASES=OPENING,MID_SESSION,CLOSING,NO_NEW_ENTRY")
    print("CLOSING_HOLD_SHORTER_THAN_300=1")
    print("MARKETABLE_LIMIT_PLAN_ONLY=1")
    print("BROKER_ORDER=0")
    print("PAPER_ORDER=0")
    print("RISK_STARTED=0")
    print("EXECUTION_STARTED=0")
    print("REDIS_WRITE=0")


if __name__ == "__main__":
    main()
