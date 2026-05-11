# REPLAY-DATA-A74 Lane C stem-equivalence repair integrity gate only

{
  "actual_nested_run_dir": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
  "advisories": [
    "Stale-leg failure is now repaired by explicit Lane C stem-equivalence behavior plus A70-R1 dataset contract.",
    "This gate only clears the integrity naming blocker; it does not clear economics/PnL readiness.",
    "A73-R2 still found no fill-bearing dataset, so economics/backtest remains blocked unless a proper fill-bearing dataset is built/admitted."
  ],
  "batch": "REPLAY-DATA-A74",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "INTEGRITY_NAMING_BLOCKER_CLEARED_FULL_SYSTEM_ECONOMICS_STILL_BLOCKED",
  "command_executed": false,
  "current_replay_run_sha256": "7ab181c51f2e55a9938cd36fd1ee520fd04caaeb0edb0d508defa5158457f482",
  "dataset_admitted_for_backtest": false,
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "expected_replay_run_sha256": "7ab181c51f2e55a9938cd36fd1ee520fd04caaeb0edb0d508defa5158457f482",
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "integrity_gate_only": true,
  "integrity_gate_pass": true,
  "integrity_report": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/03_integrity_report.json",
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "STOP_OR_BUILD_FILL_BEARING_DATASET_BEFORE_BACKTEST",
  "orders_sent": false,
  "other_failed_integrity_checks": [],
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "source_a67": "run/proofs/proof_replay_data_a67_post_execution_shadow_audit_next_scope_precheck_20260510T142850Z.json",
  "source_a70_r1": "run/proofs/proof_replay_data_a70_r1_stem_alias_contract_patch_20260510T150529Z.json",
  "source_r5bq": "run/proofs/proof_batch30j_r5bq_r3_exact_regex_anchor_patch_latest.json",
  "source_r5br": "run/proofs/proof_batch30j_r5br_no_execution_stem_equivalence_fixture_validation_latest.json",
  "source_r5br_report": "run/audits/batch30j_r5br_no_execution_stem_equivalence_fixture_validation_20260510_210224/r5br_fixture_validation_report.json",
  "stale_leg_check": {
    "check_name": "stale_leg_detection",
    "details": {
      "missing_stems": [
        "fut_ticks",
        "opt_ticks"
      ],
      "present_stems": [
        "execution_shadow_candidate",
        "features_rows_candidate",
        "health_features",
        "quote_ticks_mme_fut_stream",
        "quote_ticks_mme_opt_stream",
        "reconstruction_todo",
        "risk_outputs_candidate",
        "source_manifest",
        "strategy_decisions_candidate"
      ],
      "required_stems": [
        "fut_ticks",
        "opt_ticks"
      ]
    },
    "finished_at": "2026-05-10T14:25:16Z",
    "message": "stale_leg_detection real check failed",
    "started_at": "2026-05-10T14:25:16Z",
    "verdict": "fail"
  },
  "stem_alias_contract": "etc/replay/datasets/stem_alias_contract_v1.json",
  "stem_equivalence_ok": true,
  "verdict": "PASS_A74_LANE_C_STEM_REPAIR_INTEGRITY_GATE",
  "warning_count": 0,
  "warnings": []
}
