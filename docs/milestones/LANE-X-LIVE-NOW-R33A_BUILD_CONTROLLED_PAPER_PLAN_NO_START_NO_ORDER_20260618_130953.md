# R33A controlled-paper plan
- timestamp: 2026-06-18T13:09:53+05:30
- mode: PLAN_ONLY_NO_START_NO_ORDER
- purpose: derive fresh one-event controlled-paper launcher from current safe surfaces
=== SAFETY BEFORE ===
=== PROCESS SNAPSHOT ===
=== BUILD PLAN FROM CURRENT STREAMS ===
=== R33A PLAN FILE ===
{
  "classification": "LANE_X_R33A_CONTROLLED_PAPER_PLAN_NO_START_NO_ORDER",
  "controlled_paper_plan": {
    "action": "ENTER_PUT",
    "family": "AUTO",
    "instrument_token": "14432002",
    "live_broker_allowed": false,
    "lots": 1,
    "max_events": 1,
    "option_symbol": "NIFTY2662324050PE",
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
    "snapshot_sync_ok": false,
    "snapshot_valid": false,
    "snapshot_validity": "MARKETDATA_INCOMPLETE_OR_UNSYNCED",
    "stage_data_quality_ok": false,
    "stage_data_valid": false,
    "stage_tradability_ok": true,
    "stream_has_family_frames_json": true
  },
  "gate_ok": false,
  "latest_decision": {
    "action": "HOLD",
    "activation_candidate_count": "2",
    "activation_reason": "candidate_observed_dry_run",
    "candidate_present_shadow": "1",
    "candidate_true_shadow": "1",
    "family": "AUTO",
    "reason": "hold_only_family_features_consumer_bridge",
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
  "selected_option": {
    "delta_3": -0.5,
    "depth_ok": false,
    "depth_total": 12870,
    "ltp": 112.75,
    "micro_edge": null,
    "microprice": null,
    "ofi_ratio_proxy": null,
    "response_efficiency": 2.500000000000142,
    "selected_option_present": true,
    "selected_option_tradability_ok": true,
    "side": "PUT",
    "spread": 0.20000000000000284,
    "spread_ratio": 0.001775410563692879,
    "tradability_ok": true
  },
  "verdict": "REVIEW_R33A_PLAN_NOT_READY_NO_START_NO_ORDER",
  "xlen": {
    "decisions": 1197,
    "execution": 0,
    "features": 2042,
    "orders": 0,
    "risk": 0,
    "trades": 0
  }
}=== LAUNCH SCRIPT HEAD / NOT RUN ===
=== CONTROLLED ROUTE PREFLIGHT ONLY / NO START ===
=== FINAL OBSERVE PSTATUS ===
=== FINAL PROCESS ===

## R33A verdict
REVIEW_R33A_PLAN_NOT_READY_NO_START_NO_ORDER
- plan_rc=0
- runtime_started=NO
- paper_armed=NO
- order_attempted=NO
- launch_script=run/audits/LANE-X-LIVE-NOW-R33A_BUILD_CONTROLLED_PAPER_PLAN_NO_START_NO_ORDER_20260618_130953/R33B_RUN_ONE_EVENT_CONTROLLED_PAPER_REQUIRES_EXPLICIT_APPROVAL.sh
