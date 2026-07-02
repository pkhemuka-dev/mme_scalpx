# LANE-B-R2F_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_r1_to_r2e1_a7_single_day_replay_reproducibility_with_fingerprint_caveat_20260607_141320
2026-06-07T14:13:20+05:30

LAW=FREEZE_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

{
  "accepted_facts": {
    "candidate_count": 0,
    "dataset": "A7 normalized 2026-06-02 / B3-R61D staging dataset",
    "dominant_blocker": "economics_fail / no_entry_condition",
    "feature_rows": 134035,
    "fingerprint_caveat": "dataset_fingerprint and input_fingerprint differ between old B3-R61D and new R2C, but candidate audit and blocker distribution outputs reproduced.",
    "fut_ticks": 21808,
    "opt_ticks": 112227,
    "output_reproduced_vs_b3r61d": true,
    "pnl_grade": false,
    "pnl_grade_reason": "current scope is feeds_features_strategy and produced zero candidates/trades; strategy-wise PnL requires risk/execution-shadow scope and simulated fills.",
    "single_day_replay_smoke_passed": true,
    "strategy_rows": 134035,
    "trade_count": 0
  },
  "freeze_scope": "R1 through R2E1",
  "lane": "Lane B Replay Module Development / Replay Readiness",
  "next_route": {
    "next_batch": "LANE-B-R3_RISK_EXECUTION_SHADOW_PNL_READINESS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER",
    "purpose": "audit whether replay risk/execution-shadow scope and fill model can produce strategy-wise simulated PnL safely"
  },
  "status": "review",
  "summary": {
    "R1A_recovery": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "REVIEW_R1_ARTIFACT_INCOMPLETE_RERUN_SHORT_BASELINE_AUDIT_NEEDED",
      "latest_run_dir": null,
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R1A_RECOVER_R1_SURFACE_AUDIT_ARTIFACTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_121122.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": null
    },
    "R1_surface_baseline": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_LANE_B_R1_REPLAY_SURFACE_BASELINE_READY_FOR_R2_OFFLINE_SMOKE",
      "latest_run_dir": null,
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R1_REPLAY_SURFACE_BASELINE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_120747.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2A_locator": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2A_LOCATOR_COMPLETE_REVIEW_OUTPUT_FOR_R2B_EXACT_OFFLINE_SMOKE",
      "latest_run_dir": null,
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R2A_REPLAY_DATASET_AND_PREVIOUS_RUN_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_134930.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2B_cli_abi": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2B_CLI_ABI_VISIBLE_READY_TO_WRITE_EXACT_R2C_OFFLINE_SMOKE_COMMAND",
      "latest_run_dir": null,
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2C_offline_smoke": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2C_OFFLINE_REPLAY_SMOKE_OUTPUTS_CREATED",
      "latest_run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738.json",
      "redis_delete": false,
      "replay_executed": true,
      "risk_execution_start": false
    },
    "R2D_artifact_audit": {
      "audited_run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
      "broker_order": false,
      "classification": "PASS_R2D_R2C_ARTIFACT_SHAPE_COUNT_AUDIT_COMPLETE",
      "latest_run_dir": null,
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R2D_R2C_REPLAY_ARTIFACT_SHAPE_COUNT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140338.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2E1_fingerprint_explained": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "PASS_R2E1_DIFF_IS_FINGERPRINT_PROVENANCE_ONLY_OUTPUTS_REPRODUCED",
      "latest_run_dir": null,
      "new_run_dir": null,
      "old_run_dir": null,
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R2E1_FINGERPRINT_PROVENANCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141109.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    },
    "R2E_compare_review": {
      "audited_run_dir": null,
      "broker_order": false,
      "classification": "REVIEW_R2E_R2C_DIFFERS_FROM_FROZEN_B3R61D_INSPECT_DIFFS",
      "latest_run_dir": null,
      "new_run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
      "old_run_dir": "run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7",
      "paper_live": false,
      "patch_applied": false,
      "proof": "run/proofs/LANE-B-R2E_COMPARE_R2C_VS_B3R61D_REPLAY_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140836.json",
      "redis_delete": false,
      "replay_executed": false,
      "risk_execution_start": false
    }
  }
}
FREEZE_RC=0

CLASSIFICATION=REVIEW_R2F_FREEZE_PRECONDITION_MISSING
