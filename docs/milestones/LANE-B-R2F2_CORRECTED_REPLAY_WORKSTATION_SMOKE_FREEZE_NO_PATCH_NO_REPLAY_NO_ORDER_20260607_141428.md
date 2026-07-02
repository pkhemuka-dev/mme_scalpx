# LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428
2026-06-07T14:14:28+05:30

LAW=CORRECTED_FREEZE_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

NOTE=R1A recovery REVIEW and R2E initial compare REVIEW are non-terminal because R1 PASS and R2E1 PASS supersede them.

{
  "accepted_facts": {
    "candidate_count": 0,
    "dataset": "A7 normalized 2026-06-02 / B3-R61D staging dataset",
    "dominant_blocker": "economics_fail / no_entry_condition",
    "feature_rows": 134035,
    "fingerprint_caveat": "old and new dataset/input fingerprints differ, but candidate audit and blocker distribution reproduced exactly",
    "fut_ticks": 21808,
    "opt_ticks": 112227,
    "output_reproduced_vs_b3r61d": true,
    "pnl_grade": false,
    "pnl_grade_reason": "feeds_features_strategy scope produced zero candidates/trades; strategy-wise PnL requires risk/execution-shadow scope and simulated fills",
    "single_day_replay_smoke_passed": true,
    "strategy_rows": 134035,
    "trade_count": 0
  },
  "next_batch": "LANE-B-R3_RISK_EXECUTION_SHADOW_PNL_READINESS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER",
  "required_terminal_checks": {
    "R1": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_LANE_B_R1_REPLAY_SURFACE_BASELINE_READY_FOR_R2_OFFLINE_SMOKE",
      "latest_run_dir": null,
      "paper_live": false,
      "pass_ok": true,
      "proof": "run/proofs/LANE-B-R1_REPLAY_SURFACE_BASELINE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_120747.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2A": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2A_LOCATOR_COMPLETE_REVIEW_OUTPUT_FOR_R2B_EXACT_OFFLINE_SMOKE",
      "latest_run_dir": null,
      "paper_live": false,
      "pass_ok": true,
      "proof": "run/proofs/LANE-B-R2A_REPLAY_DATASET_AND_PREVIOUS_RUN_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_134930.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2B": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2B_CLI_ABI_VISIBLE_READY_TO_WRITE_EXACT_R2C_OFFLINE_SMOKE_COMMAND",
      "latest_run_dir": null,
      "paper_live": false,
      "pass_ok": true,
      "proof": "run/proofs/LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2C": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2C_OFFLINE_REPLAY_SMOKE_OUTPUTS_CREATED",
      "latest_run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
      "paper_live": false,
      "pass_ok": true,
      "proof": "run/proofs/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738.json",
      "redis_delete": false,
      "replay_executed": true,
      "risk_execution_start": false
    },
    "R2D": {
      "audited_run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
      "broker_order": false,
      "classification": "PASS_R2D_R2C_ARTIFACT_SHAPE_COUNT_AUDIT_COMPLETE",
      "latest_run_dir": null,
      "paper_live": false,
      "pass_ok": true,
      "proof": "run/proofs/LANE-B-R2D_R2C_REPLAY_ARTIFACT_SHAPE_COUNT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140338.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2E1": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2E1_DIFF_IS_FINGERPRINT_PROVENANCE_ONLY_OUTPUTS_REPRODUCED",
      "latest_run_dir": null,
      "paper_live": false,
      "pass_ok": true,
      "proof": "run/proofs/LANE-B-R2E1_FINGERPRINT_PROVENANCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141109.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    }
  },
  "status": "ready_to_freeze",
  "superseded_nonterminal_reviews": {
    "R1A": "recovery helper only; actual R1 PASS is terminal",
    "R2E": "initial compare showed fingerprint diff; R2E1 explained it as provenance-only"
  }
}
FREEZE_RC=0

CLASSIFICATION=PASS_R2F2_REPLAY_WORKSTATION_SMOKE_FREEZE_WITH_FINGERPRINT_CAVEAT
