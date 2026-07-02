# R33A2 wait stable-green controlled-paper plan
- timestamp: 2026-06-18T13:31:27+05:30
- mode: PLAN_ONLY_NO_START_NO_ORDER
- purpose: require stable-green feature gate before preparing runnable R33B
=== SAFETY BEFORE ===
=== PROCESS SNAPSHOT ===
=== WATCH GREEN GATE AND BUILD PLAN ONLY IF STABLE ===
=== R33A2 PLAN FILE ===
{
  "bad_runtime": [],
  "classification": "LANE_X_R33A2_WAIT_STABLE_GREEN_PLAN_NO_START_NO_ORDER",
  "controlled_paper_plan": {
    "action": "ENTER_PUT",
    "family": "AUTO",
    "instrument_token": "14432258",
    "live_broker_allowed": false,
    "lots": 1,
    "max_events": 1,
    "option_symbol": "NIFTY2662324100CE",
    "paper_only": true,
    "side": "PUT",
    "stop_after_one": true
  },
  "feature_gate": {
    "consumer_hold_only": true,
    "consumer_provider_ready_classic": false,
    "consumer_safe_to_consume": false,
    "consumer_tradability_ok": true,
    "contract_top_level_r20_absent": true,
    "family_frames_key_count": 10,
    "provider_ready_classic": false,
    "provider_ready_miso": false,
    "snapshot_skew_ms": 1000,
    "snapshot_sync_ok": false,
    "snapshot_valid": false,
    "snapshot_validity": "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
    "stage_data_quality_ok": false,
    "stage_data_valid": false,
    "stage_tradability_ok": true,
    "stream_has_family_frames_json": true
  },
  "gate_ok": false,
  "history_tail": [
    {
      "controlled_paper_plan": {
        "action": "ENTER_PUT",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "PUT",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": true,
        "consumer_provider_ready_classic": false,
        "consumer_safe_to_consume": false,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": false,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 1000,
        "snapshot_sync_ok": false,
        "snapshot_valid": false,
        "snapshot_validity": "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
        "stage_data_quality_ok": false,
        "stage_data_valid": false,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 17,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "PUT"
      },
      "needs_token_symbol": false,
      "runtime_clean": false,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2493,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_PUT",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "PUT",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": false,
        "consumer_provider_ready_classic": true,
        "consumer_safe_to_consume": true,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 0,
        "snapshot_sync_ok": true,
        "snapshot_valid": true,
        "snapshot_validity": "OK",
        "stage_data_quality_ok": true,
        "stage_data_valid": true,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 18,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "PUT"
      },
      "needs_token_symbol": false,
      "runtime_clean": false,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2495,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_CALL",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "CALL",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": false,
        "consumer_provider_ready_classic": true,
        "consumer_safe_to_consume": true,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 0,
        "snapshot_sync_ok": true,
        "snapshot_valid": true,
        "snapshot_validity": "OK",
        "stage_data_quality_ok": true,
        "stage_data_valid": true,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 19,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "CALL"
      },
      "needs_token_symbol": false,
      "runtime_clean": false,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2497,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_CALL",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "CALL",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": true,
        "consumer_provider_ready_classic": false,
        "consumer_safe_to_consume": false,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": false,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 1000,
        "snapshot_sync_ok": false,
        "snapshot_valid": false,
        "snapshot_validity": "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
        "stage_data_quality_ok": false,
        "stage_data_valid": false,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 20,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "CALL"
      },
      "needs_token_symbol": false,
      "runtime_clean": false,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2498,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_CALL",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "CALL",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": false,
        "consumer_provider_ready_classic": true,
        "consumer_safe_to_consume": true,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 0,
        "snapshot_sync_ok": true,
        "snapshot_valid": true,
        "snapshot_validity": "OK",
        "stage_data_quality_ok": true,
        "stage_data_valid": true,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 21,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "CALL"
      },
      "needs_token_symbol": false,
      "runtime_clean": false,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2500,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_CALL",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "CALL",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": false,
        "consumer_provider_ready_classic": true,
        "consumer_safe_to_consume": true,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 0,
        "snapshot_sync_ok": true,
        "snapshot_valid": true,
        "snapshot_validity": "OK",
        "stage_data_quality_ok": true,
        "stage_data_valid": true,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 22,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "CALL"
      },
      "needs_token_symbol": false,
      "runtime_clean": false,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2502,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_CALL",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "CALL",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": false,
        "consumer_provider_ready_classic": true,
        "consumer_safe_to_consume": true,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": true,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 0,
        "snapshot_sync_ok": true,
        "snapshot_valid": true,
        "snapshot_validity": "OK",
        "stage_data_quality_ok": true,
        "stage_data_valid": true,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 23,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "CALL"
      },
      "needs_token_symbol": false,
      "runtime_clean": true,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2503,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "controlled_paper_plan": {
        "action": "ENTER_PUT",
        "family": "AUTO",
        "instrument_token": "14432258",
        "live_broker_allowed": false,
        "lots": 1,
        "max_events": 1,
        "option_symbol": "NIFTY2662324100CE",
        "paper_only": true,
        "side": "PUT",
        "stop_after_one": true
      },
      "feature_gate": {
        "consumer_hold_only": true,
        "consumer_provider_ready_classic": false,
        "consumer_safe_to_consume": false,
        "consumer_tradability_ok": true,
        "contract_top_level_r20_absent": true,
        "family_frames_key_count": 10,
        "provider_ready_classic": false,
        "provider_ready_miso": false,
        "snapshot_skew_ms": 1000,
        "snapshot_sync_ok": false,
        "snapshot_valid": false,
        "snapshot_validity": "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
        "stage_data_quality_ok": false,
        "stage_data_valid": false,
        "stage_tradability_ok": true,
        "stream_has_family_frames_json": true
      },
      "gate_ok": false,
      "iteration": 24,
      "latest_decision": {
        "action": "ENTER_CALL",
        "activation_candidate_count": null,
        "activation_reason": null,
        "candidate_present_shadow": null,
        "candidate_true_shadow": null,
        "family": "AUTO",
        "reason": null,
        "side": "PUT"
      },
      "needs_token_symbol": false,
      "runtime_clean": true,
      "xlen": {
        "decisions": 1,
        "execution": 0,
        "features": 2505,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    }
  ],
  "iteration": 24,
  "latest_decision": {
    "action": "ENTER_CALL",
    "activation_candidate_count": null,
    "activation_reason": null,
    "candidate_present_shadow": null,
    "candidate_true_shadow": null,
    "family": "AUTO",
    "reason": null,
    "side": "PUT"
  },
  "needs_token_symbol": false,
  "position": {
    "avg_price": "",
    "broker_order_id": "",
    "decision_id": "",
    "entry_mode": "",
    "entry_option_symbol": "",
    "entry_option_token": "",
    "entry_strike": "",
    "entry_ts_ns": "",
    "has_position": "0",
    "mark_price": "",
    "position_side": "FLAT",
    "qty_lots": "0",
    "qty_units": "0",
    "realized_pnl_day": "0"
  },
  "ready": false,
  "runtime_clean": true,
  "selected_option": {
    "delta_3": 2.299999999999997,
    "depth_ok": false,
    "depth_total": 17225,
    "ltp": 106.85,
    "micro_edge": null,
    "microprice": null,
    "ofi_ratio_proxy": null,
    "response_efficiency": 9.199999999999989,
    "selected_option_present": true,
    "selected_option_tradability_ok": true,
    "side": "PUT",
    "spread": 0.25,
    "spread_ratio": 0.0023424689622862497,
    "tradability_ok": true
  },
  "stable_green_count": 0,
  "ts_epoch": 1781769807.0795314,
  "verdict": "REVIEW_R33A2_STABLE_GREEN_NOT_FOUND_NO_START_NO_ORDER",
  "xlen": {
    "decisions": 1,
    "execution": 0,
    "features": 2505,
    "orders": 0,
    "risk": 0,
    "trades": 0
  }
}=== LAUNCH SCRIPT PREVIEW / NOT RUN ===
=== CONTROLLED ROUTE PREFLIGHT ONLY / NO START ===
=== FINAL OBSERVE PSTATUS ===
=== FINAL PROCESS ===

## R33A2 verdict
REVIEW_R33A2_STABLE_GREEN_NOT_FOUND_NO_START_NO_ORDER
- plan_rc=0
- runtime_started=NO
- paper_armed=NO
- order_attempted=NO
- launch_script=run/audits/LANE-X-LIVE-NOW-R33A2_WAIT_STABLE_GREEN_PLAN_NO_START_NO_ORDER_20260618_133127/R33B_RUN_ONE_EVENT_CONTROLLED_PAPER_REQUIRES_EXPLICIT_APPROVAL.sh
