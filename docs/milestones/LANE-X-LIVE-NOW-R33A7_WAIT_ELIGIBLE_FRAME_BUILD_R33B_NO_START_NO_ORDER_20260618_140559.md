# R33A7 wait eligible frame
- timestamp: 2026-06-18T14:05:59+05:30
- mode: PLAN_ONLY_NO_START_NO_ORDER
- rule: only eligible=true + top_green=true + tradability_ok=true + side/symbol match
=== SAFETY BEFORE ===
=== PROCESS BEFORE ===
=== WATCH FOR ELIGIBLE FRAME / BUILD ONLY IF REAL ===
=== R33A7 PLAN FILE ===
{
  "classification": "LANE_X_R33A7_WAIT_ELIGIBLE_FRAME_BUILD_R33B_NO_START_NO_ORDER",
  "history_tail": [
    {
      "eligible_candidate_count": 0,
      "flat": true,
      "iteration": 1,
      "runtime_bad_count": 0,
      "safe_streams": true,
      "selected": null,
      "stable_count": 0,
      "xlen": {
        "decisions": 1228,
        "execution": 0,
        "features": 3138,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "eligible_candidate_count": 0,
      "flat": true,
      "iteration": 2,
      "runtime_bad_count": 0,
      "safe_streams": true,
      "selected": null,
      "stable_count": 0,
      "xlen": {
        "decisions": 1232,
        "execution": 0,
        "features": 3140,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "eligible_candidate_count": 2,
      "flat": true,
      "iteration": 3,
      "runtime_bad_count": 1,
      "safe_streams": true,
      "selected": {
        "action": "ENTER_PUT",
        "branch": "misb_put",
        "eligible": true,
        "eligible_bool": true,
        "family": "MISB",
        "instrument_token": "14432514",
        "option_price": 117.0,
        "option_symbol": "NIFTY2662324100PE",
        "path": "$consumer_view_json.family_frames.misb_put",
        "raw_symbol": "NIFTY2662324100PE",
        "runtime_mode": "NORMAL",
        "side": "PUT",
        "source_container": "family_frames",
        "stop_points": 4.0,
        "stream_id": "1781771767997-0",
        "suffix_side": "PUT",
        "target_points": 5.0,
        "top_green": true,
        "tradability_ok": true
      },
      "stable_count": 0,
      "xlen": {
        "decisions": 1234,
        "execution": 0,
        "features": 3141,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "eligible_candidate_count": 4,
      "flat": true,
      "iteration": 4,
      "runtime_bad_count": 1,
      "safe_streams": true,
      "selected": {
        "action": "ENTER_PUT",
        "branch": "misb_put",
        "eligible": true,
        "eligible_bool": true,
        "family": "MISB",
        "instrument_token": "14432514",
        "option_price": 116.6,
        "option_symbol": "NIFTY2662324100PE",
        "path": "$consumer_view_json.family_frames.misb_put",
        "raw_symbol": "NIFTY2662324100PE",
        "runtime_mode": "NORMAL",
        "side": "PUT",
        "source_container": "family_frames",
        "stop_points": 4.0,
        "stream_id": "1781771772893-0",
        "suffix_side": "PUT",
        "target_points": 5.0,
        "top_green": true,
        "tradability_ok": true
      },
      "stable_count": 0,
      "xlen": {
        "decisions": 1237,
        "execution": 0,
        "features": 3143,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "eligible_candidate_count": 4,
      "flat": true,
      "iteration": 5,
      "runtime_bad_count": 0,
      "safe_streams": true,
      "selected": {
        "action": "ENTER_PUT",
        "branch": "misb_put",
        "eligible": true,
        "eligible_bool": true,
        "family": "MISB",
        "instrument_token": "14432514",
        "option_price": 116.6,
        "option_symbol": "NIFTY2662324100PE",
        "path": "$consumer_view_json.family_frames.misb_put",
        "raw_symbol": "NIFTY2662324100PE",
        "runtime_mode": "NORMAL",
        "side": "PUT",
        "source_container": "family_frames",
        "stop_points": 4.0,
        "stream_id": "1781771772893-0",
        "suffix_side": "PUT",
        "target_points": 5.0,
        "top_green": true,
        "tradability_ok": true
      },
      "stable_count": 1,
      "xlen": {
        "decisions": 1241,
        "execution": 0,
        "features": 3144,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    },
    {
      "eligible_candidate_count": 4,
      "flat": true,
      "iteration": 6,
      "runtime_bad_count": 0,
      "safe_streams": true,
      "selected": {
        "action": "ENTER_PUT",
        "branch": "misb_put",
        "eligible": true,
        "eligible_bool": true,
        "family": "MISB",
        "instrument_token": "14432514",
        "option_price": 116.6,
        "option_symbol": "NIFTY2662324100PE",
        "path": "$consumer_view_json.family_frames.misb_put",
        "raw_symbol": "NIFTY2662324100PE",
        "runtime_mode": "NORMAL",
        "side": "PUT",
        "source_container": "family_frames",
        "stop_points": 4.0,
        "stream_id": "1781771772893-0",
        "suffix_side": "PUT",
        "target_points": 5.0,
        "top_green": true,
        "tradability_ok": true
      },
      "stable_count": 2,
      "xlen": {
        "decisions": 1244,
        "execution": 0,
        "features": 3146,
        "orders": 0,
        "risk": 0,
        "trades": 0
      }
    }
  ],
  "last_seen_candidate": {
    "action": "ENTER_PUT",
    "branch": "misb_put",
    "eligible": true,
    "eligible_bool": true,
    "family": "MISB",
    "instrument_token": "14432514",
    "option_price": 116.6,
    "option_symbol": "NIFTY2662324100PE",
    "path": "$consumer_view_json.family_frames.misb_put",
    "raw_symbol": "NIFTY2662324100PE",
    "runtime_mode": "NORMAL",
    "side": "PUT",
    "source_container": "family_frames",
    "stop_points": 4.0,
    "stream_id": "1781771772893-0",
    "suffix_side": "PUT",
    "target_points": 5.0,
    "top_green": true,
    "tradability_ok": true
  },
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
  "ready": true,
  "runtime_bad": [],
  "selected_launch_candidate": {
    "action": "ENTER_PUT",
    "branch": "misb_put",
    "eligible": true,
    "eligible_bool": true,
    "family": "MISB",
    "instrument_token": "14432514",
    "option_price": 116.6,
    "option_symbol": "NIFTY2662324100PE",
    "path": "$consumer_view_json.family_frames.misb_put",
    "raw_symbol": "NIFTY2662324100PE",
    "runtime_mode": "NORMAL",
    "side": "PUT",
    "source_container": "family_frames",
    "stop_points": 4.0,
    "stream_id": "1781771772893-0",
    "suffix_side": "PUT",
    "target_points": 5.0,
    "top_green": true,
    "tradability_ok": true
  },
  "stable_count": 2,
  "verdict": "PASS_R33A7_ELIGIBLE_STABLE_R33B_READY_REQUIRES_EXPLICIT_APPROVAL_NO_START_NO_ORDER",
  "xlen": {
    "decisions": 1244,
    "execution": 0,
    "features": 3146,
    "orders": 0,
    "risk": 0,
    "trades": 0
  }
}=== LAUNCH SCRIPT PREVIEW / NOT RUN ===
=== FINAL OBSERVE PSTATUS ===
=== FINAL PROCESS ===

## R33A7 verdict
PASS_R33A7_ELIGIBLE_STABLE_R33B_READY_REQUIRES_EXPLICIT_APPROVAL_NO_START_NO_ORDER
- plan_rc=0
- runtime_started=NO
- paper_armed=NO
- order_attempted=NO
- launch_script=run/audits/LANE-X-LIVE-NOW-R33A7_WAIT_ELIGIBLE_FRAME_BUILD_R33B_NO_START_NO_ORDER_20260618_140559/R33B_RUN_ONE_EVENT_CONTROLLED_PAPER_REQUIRES_EXPLICIT_APPROVAL.sh
