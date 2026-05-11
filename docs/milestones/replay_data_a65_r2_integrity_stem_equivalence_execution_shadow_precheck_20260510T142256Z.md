# REPLAY-DATA-A65-R2 integrity stem-equivalence repair gate

{
  "a66_preview_command_shell": ".venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z --selection-mode single_day --single-day 2026-04-17 --doctrine-mode locked --speed-mode accelerated --required-file-stems quote_ticks_mme_fut_stream,quote_ticks_mme_opt_stream --optional-file-stems features_rows_candidate,strategy_decisions_candidate,risk_outputs_candidate,execution_shadow_candidate,source_manifest,health_features --supported-suffixes .csv,.json,.jsonl --scope feeds_features_strategy_risk_execution_shadow --run-label a66_guarded_feeds_features_strategy_risk_execution_shadow_execution --run-root run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z",
  "a66_preview_generated": true,
  "a66_preview_path": "run/replay/a65_r2_execution_shadow_scope_precheck/20260510T142256Z/feeds_features_strategy_risk_execution_shadow_PREVIEW_ONLY_NOT_EXECUTED.sh",
  "artifact_audit_only": true,
  "batch": "REPLAY-DATA-A65-R2",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "candidate_count": 0,
  "classification": "PASS_A65_GATE_ONLY_A66_PREVIEW_GENERATED_NOT_EXECUTED",
  "command_executed": false,
  "economics_pnl_evaluation_allowed": false,
  "execution_shadow_execution_started": false,
  "execution_shadow_precheck_ok": true,
  "failed_integrity_check": {
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
    "finished_at": "2026-05-10T14:04:12Z",
    "message": "stale_leg_detection real check failed",
    "started_at": "2026-05-10T14:04:12Z",
    "verdict": "fail"
  },
  "features_row_count": 165650,
  "full_engine_replay_allowed": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "REPLAY-DATA-A66 guarded execution-shadow gate/execution only if A65-R2 PASS is accepted",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "passed_integrity_checks": [
    "heartbeat_integrity",
    "hash_freshness",
    "snapshot_sync_validity",
    "reset_cleanliness",
    "reproducibility_proof"
  ],
  "risk_action_breakdown": {
    "HOLD": 165650
  },
  "risk_row_count": 165650,
  "source_a65": "run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json",
  "stem_equivalence": {
    "fut_ticks": "quote_ticks_mme_fut_stream",
    "opt_ticks": "quote_ticks_mme_opt_stream"
  },
  "strategy_action_breakdown": {
    "HOLD": 165650
  },
  "strategy_row_count": 165650,
  "trade_count": 0,
  "verdict": "PASS_A65_R2_STEM_EQUIVALENCE_EXECUTION_SHADOW_PRECHECK",
  "warning_count": 2,
  "warnings": [
    "A64 integrity failure accepted only as stale-leg legacy stem-name mismatch: fut_ticks/opt_ticks equivalent to quote_ticks_mme_fut_stream/quote_ticks_mme_opt_stream for this dataset.",
    "A65-R2 is gate-only; A66 preview generated but execution-shadow not started."
  ]
}
