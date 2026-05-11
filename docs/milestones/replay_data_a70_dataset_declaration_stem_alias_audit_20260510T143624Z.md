# REPLAY-DATA-A70 dataset declaration + stem-alias contract audit only

{
  "actual_nested_run_dir": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
  "advisories": [
    "A70 freezes the required stem-alias contract shape only; it does not patch source files.",
    "Next valid action is A70-R1/A71 depending on whether you want to patch dataset declaration/profile contract or audit economics fields first.",
    "Full-system/economics remain blocked until integrity contract and economics readiness are repaired separately."
  ],
  "batch": "REPLAY-DATA-A70",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "STEM_ALIAS_CONTRACT_READY_FOR_SEPARATE_PATCH_FULL_SYSTEM_ECONOMICS_STILL_BLOCKED",
  "command_executed": false,
  "contract_patch_applied": false,
  "contract_patch_required": true,
  "dataset_declaration_audit_only": true,
  "dataset_profile_findings": {
    "dataset_identity_observed": "admitted_quote_only",
    "dataset_summary_path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/01_dataset_summary.json",
    "economics_evaluable_observed": "declared_field_present",
    "integrity_path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/03_integrity_report.json",
    "manifest_path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/00_manifest.json",
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
    ],
    "scope_profile_path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/02_scope_profile.json",
    "source_mode_observed": "quote_only_recorded"
  },
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "REPLAY-DATA-A70-R1 stem-alias dataset declaration/profile contract patch only",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "source_a68": "run/proofs/proof_replay_data_a68_full_system_economics_readiness_audit_20260510T143258Z.json",
  "source_a69": "run/proofs/proof_replay_data_a69_dataset_integrity_economics_repair_plan_20260510T143444Z.json",
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
  "stem_alias_contract": {
    "allowed_use": [
      "integrity stale-leg interpretation",
      "dataset declaration/profile repair",
      "quote-only replay admission clarity"
    ],
    "canonical_equivalences": {
      "fut_ticks": "quote_ticks_mme_fut_stream",
      "opt_ticks": "quote_ticks_mme_opt_stream"
    },
    "contract_id": "replay_dataset_stem_alias_v1",
    "contract_scope": "dataset_declaration_and_integrity_interpretation_only",
    "forbidden_use": [
      "do not waive full-system/economics readiness",
      "do not imply PnL/economics eligibility",
      "do not authorize full_system_replay",
      "do not authorize economics_pnl_evaluation",
      "do not alter production/live names"
    ]
  },
  "verdict": "PASS_A70_STEM_ALIAS_CONTRACT_AUDIT_ONLY",
  "warning_count": 0,
  "warnings": []
}
