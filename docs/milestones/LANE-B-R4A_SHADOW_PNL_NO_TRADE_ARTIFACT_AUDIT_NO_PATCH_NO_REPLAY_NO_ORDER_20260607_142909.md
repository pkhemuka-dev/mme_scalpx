# LANE-B-R4A_SHADOW_PNL_NO_TRADE_ARTIFACT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_142909
2026-06-07T14:29:10+05:30

LAW=ARTIFACT_AUDIT_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

R4_PROOF=run/proofs/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249.json

{
  "candidate_count": 0,
  "current_dataset_pnl_grade": false,
  "current_dataset_pnl_grade_reason": "zero candidates, zero trades, zero fills; no strategy-wise PnL can be inferred from this dataset",
  "execution_shadow_action_breakdown": {},
  "execution_shadow_filled_count": 0,
  "execution_shadow_row_count": 134035,
  "feature_leg_breakdown": {
    "CALL_ATM": 56400,
    "FUTURES": 21808,
    "PUT_ATM": 55827
  },
  "feature_side_breakdown": {
    "CALL": 56400,
    "CONTEXT": 21808,
    "PUT": 55827
  },
  "integrity_verdict": "pass",
  "next_requirement_for_real_strategy_pnl": "Need replay run where candidate_count > 0 and execution_shadow_filled_count > 0, either from a valid trade dataset or controlled baseline-vs-shadow patch-impact replay.",
  "pnl_total": null,
  "r4_proof": "run/proofs/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249.json",
  "risk_action_breakdown": {
    "HOLD": 134035
  },
  "risk_row_count": 134035,
  "risk_vetoed_true_count": 0,
  "run_dir": "run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4",
  "scope": "feeds_features_strategy_risk_execution_shadow",
  "strategy_action_breakdown": {
    "HOLD": 134035
  },
  "strategy_wise_pnl_status": {
    "MISB": "NO_TRADE_NO_PNL",
    "MISC": "NO_TRADE_NO_PNL",
    "MISO": "NO_TRADE_NO_PNL_OR_NOT_ELIGIBLE_ON_THIS_DATASET",
    "MISR": "NO_TRADE_NO_PNL",
    "MIST": "NO_TRADE_NO_PNL"
  },
  "trade_count": 0
}
AUDIT_RC=0

CLASSIFICATION=REVIEW_R4A_SHADOW_PNL_AUDIT_INCOMPLETE
