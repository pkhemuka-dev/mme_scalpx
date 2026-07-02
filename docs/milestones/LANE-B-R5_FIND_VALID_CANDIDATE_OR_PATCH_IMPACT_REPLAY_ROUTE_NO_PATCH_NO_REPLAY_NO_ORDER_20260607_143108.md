# LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108
2026-06-07T14:31:08+05:30

LAW=ROUTE_SELECTION_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Latest R4A2 freeze
R4A2=run/proofs/LANE-B-R4A2_CORRECTED_SHADOW_PNL_NO_TRADE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143017.json
{
  "tag": "LANE-B-R4A2_CORRECTED_SHADOW_PNL_NO_TRADE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143017",
  "classification": "PASS_R4A2_SHADOW_PNL_SURFACE_EXISTS_CURRENT_DATASET_NO_TRADE_NO_PNL_FREEZE",
  "patch_applied": false,
  "replay_executed": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "current_dataset_pnl_grade": false,
  "strategy_wise_pnl_status": "NO_TRADE_NO_PNL",
  "next_batch": "LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER",
  "report": "run/audits/LANE-B-R4A2_CORRECTED_SHADOW_PNL_NO_TRADE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143017_report.md"
}

## Replay run summary inventory
{
  "positive_candidate_trade_or_fill_count": 0,
  "positive_runs": [],
  "recent_runs": [
    {
      "candidate_count": 0,
      "dataset_id": "raw_aa10n_feed_input_adapter_export_20260501_193317",
      "execution_shadow_filled": 0,
      "execution_shadow_rows": 0,
      "feature_leg_breakdown": {},
      "feature_rows": 0,
      "feature_side_breakdown": {},
      "integrity": "fail",
      "path": "run/replay/raw_aa8_larger_balanced_candidate_20260501_190008/replay_locked_single_day_raw_aa8_larger_balanced_candidate_20260501_190008_20260501_141229_d2022499/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 0,
      "run_id": "replay_locked_single_day_raw_aa8_larger_balanced_candidate_20260501_190008_20260501_141229_d2022499",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {},
      "strategy_rows": 0,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_baseline_true_cmp_20260418_125113_2e52d119/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_baseline_true_cmp_20260418_125113_2e52d119",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phase_a4_true_owner_rerun_20260418_173649_9e3c2c88/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phase_a4_true_owner_rerun_20260418_173649_9e3c2c88",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131641_b9df3a1c/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131641_b9df3a1c",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131325_08d2c6e3/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea1_features_check_20260418_131325_08d2c6e3",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea3_baseline_true_cmp_20260418_132241_026c0f38/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea3_baseline_true_cmp_20260418_132241_026c0f38",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": null,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_run_summary_check_20260418_114949_ec504cc6/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_run_summary_check_20260418_114949_ec504cc6",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": null
    },
    {
      "candidate_count": null,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_run_summary_csv_check_20260418_115349_fa53cbad/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_run_summary_csv_check_20260418_115349_fa53cbad",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": null
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_locked_single_day_run_summary_fill_check_20260418_115722_7b941385/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_locked_single_day_run_summary_fill_check_20260418_115722_7b941385",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131707_d86701a2/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131707_d86701a2",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_shadow_single_day_phasea3_shadow_true_cmp_20260418_132241_2cacf973/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_shadow_single_day_phasea3_shadow_true_cmp_20260418_132241_2cacf973",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_shadow_single_day_shadow_true_cmp_20260418_124920_bb12f0ac/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_shadow_single_day_shadow_true_cmp_20260418_124920_bb12f0ac",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "replay_dataset_2026_04_17",
      "execution_shadow_filled": null,
      "execution_shadow_rows": null,
      "feature_leg_breakdown": {
        "CALL_ATM": 2,
        "FUTURES": 2
      },
      "feature_rows": 4,
      "feature_side_breakdown": {
        "CALL": 2,
        "CONTEXT": 2
      },
      "integrity": "pass",
      "path": "run/replay/replay_shadow_single_day_shadow_true_cmp_20260418_124924_96d4d245/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 4,
      "run_id": "replay_shadow_single_day_shadow_true_cmp_20260418_124924_96d4d245",
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "strategy_actions": {
        "HOLD": 4
      },
      "strategy_rows": 4,
      "trade_count": 0
    },
    {
      "candidate_count": 0,
      "dataset_id": "session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z",
      "execution_shadow_filled": 0,
      "execution_shadow_rows": 0,
      "feature_leg_breakdown": {},
      "feature_rows": 0,
      "feature_side_breakdown": {},
      "integrity": "fail",
      "path": "run/replay/selector_only_executions/replay_data_a30_guarded_selector_only_cleaned_dataset_20260510T040904Z/replay_run_root/replay_locked_single_day_a30_guarded_selector_only_cleaned_dataset_20260510_040910_75516f7a/artifacts/10_run_summary.json",
      "pnl_total": null,
      "risk_rows": 0,
      "run_id": "replay_locked_single_day_a30_guarded_selector_only_cleaned_dataset_20260510_040910_75516f7a",
      "scope": "feeds_only",
      "strategy_actions": {},
      "strategy_rows": 0,
      "trade_count": 0
    }
  ],
  "summary_count": 49
}
INVENTORY_RC=0

## Existing candidate/trade/pnl-looking artifacts without full read
docs/milestones/2026-04-25_batch11_activation_candidate_action_corrective.md
docs/milestones/2026-04-25_batch1_strategy_family_leaf_candidate_contract_freeze_final.md
docs/milestones/2026-04-25_offline_static_freeze_candidate_archive_20260425_133816.md
docs/milestones/2026-04-25_replay_integrity_execution_shadow_persist_20260425_153204.md
docs/milestones/2026-04-25_replay_integrity_execution_shadow_writepoint_20260425_152919.md
docs/milestones/2026-04-26_batch25p_candidate_metadata_standardization.md
docs/milestones/2026-05-04_batch26o15_activation_candidate_surface_audit.md
docs/milestones/2026-05-05_batch26o17_activation_candidate_extraction.md
docs/milestones/2026-05-07_batch26o23_e_no_candidate_root_cause_review.md
docs/milestones/A6-PAPER-AFTERMARKET-R18-R3_short_read_only_latest_stream_pfeeds_pstack_candidate_audit_no_start_no_order_no_paper_20260520_000533.md
docs/milestones/A6-PAPER-AFTERMARKET-R18_pfeeds_pstack_backtest_data_and_strategy_candidate_audit_no_start_no_order_no_paper_20260520_000152.md
docs/milestones/A6-PAPER-R17M-R2B_pfeeds_pstack_readiness_and_candidate_audit_after_r17m_r2_block_no_risk_no_execution_no_order_20260520_094641.md
docs/milestones/A6-PAPER-R17M-R2J_read_only_running_stack_lock_owner_and_candidate_ratification_after_r2i_no_start_no_kill_no_delete_no_order_20260520_101536.md
docs/milestones/A6-PAPER-R17O-R1_fresh_live_candidate_scope_audit_rerun_no_start_no_order_no_enablement_20260520_110014.md
docs/milestones/A6-PAPER-R17O-R2_extended_fresh_live_candidate_watch_no_start_no_order_no_enablement_20260520_130111.md
docs/milestones/A6-PAPER-R17O-R2_extended_fresh_live_candidate_watch_no_start_no_order_no_enablement_20260520_130526.md
docs/milestones/A6-PAPER-R17O-R3_candidate_absence_forensics_from_live_decisions_no_start_no_order_no_enablement_20260520_131223.md
docs/milestones/A6-PAPER-R17O-R4_fresh_candidate_audit_after_strategy_decision_recovery_with_diagnostic_limitation_no_start_no_order_20260520_144126.md
docs/milestones/A6-PAPER-R17O_fresh_live_candidate_scope_audit_before_any_paper_order_no_start_no_order_no_enablement_20260520_105628.md
docs/milestones/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133.md
docs/milestones/B1-PROFIT-CLASSIC-R0_CLASSIC_READY_NO_CANDIDATE_ROOT_CAUSE_AUDIT_NO_ORDER_after_market_audit_classic_ready_decisions_why_no_mist_misb_misc_misr_candidate_no_start_no_order_20260520_231628.md
docs/milestones/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701.md
docs/milestones/B1-PROFIT-LIVE-R0_CLASSIC_CANDIDATE_AND_DHAN_CONTEXT_GROWTH_AUDIT_NO_ORDER_live_session_audit_pfeeds_pstack_dhan_context_classic_candidate_growth_no_patch_no_start_no_order_20260521_094211.md
docs/milestones/B1-PROFIT-LIVE-R1_LOCK_PROCESS_AND_CLASSIC_READY_NO_CANDIDATE_TRIAGE_NO_ORDER_read_only_triage_execution_lock_service_detection_and_classic_ready_zero_candidate_no_start_no_kill_no_delete_no_order_20260521_094428.md
docs/milestones/B1-PROFIT-LIVE-R34W_DURABLE_STREAM_TAIL_CURRENT_ONLY_NO_ORDER_current_only_read_only_xread_tail_no_backfill_no_patch_no_start_no_stop_no_redis_write_20260522_125839.md
docs/milestones/B1-PROFIT-LIVE-R38F_live_observe_only_fallback_candidate_surface_preflight_no_paper_no_order_20260529_094258.md
docs/milestones/B1-PROFIT-LIVE-R38J_read_only_family_side_candidate_selector_after_failover_preflight_no_order_no_paper_20260529_095340.md
docs/milestones/B1-PROFIT-LIVE-R38K_read_only_classic_candidate_watch_after_r38j_no_order_no_paper_20260529_095507.md
docs/milestones/B1-PROFIT-LIVE-R38L_read_only_near_miss_blocker_audit_after_no_candidate_watch_no_order_no_paper_20260529_100903.md
docs/milestones/B1-PROFIT-LIVE-R38L_read_only_near_miss_blocker_audit_after_no_candidate_watch_no_order_no_paper_20260529_101116.md
docs/milestones/B1-PROFIT-LIVE-R38X-R2_strict_json_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_195424.md
docs/milestones/B1-PROFIT-LIVE-R38X_offline_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_194922.md
docs/milestones/B1-PROFIT-LIVE-R38ZH-R2_offline_patched_candidate_reevaluation_after_stale_feed_cleanup_no_patch_no_order_20260531_225914.md
docs/milestones/B1-PROFIT-LIVE-R39E_A7_NARROW_PROVIDER_RUNTIME_COMPAT_ALIAS_PATCH_NO_START_NO_STOP_NO_ORDER_wrap_strategy_provider_runtime_validation_with_alias_backfill_after_r39d_new_error_20260602_095012.md
docs/milestones/B1-PROFIT-LIVE-R39G_A7_PATCH_EXACT_PROVIDER_RUNTIME_VALIDATOR_SEAM_NO_START_NO_STOP_NO_ORDER_contracts_py_validate_provider_runtime_alias_backfill_after_r39f_exact_seam_20260602_095527.md
docs/milestones/B1-PROFIT-LIVE-R39H_A7_PATCH_PROVIDER_RUNTIME_MISSING_KEYS_BLOCK_NO_START_NO_STOP_NO_ORDER_contracts_py_exact_missing_keys_block_alias_backfill_after_r39g_def_not_found_20260602_095711.md
docs/milestones/B1-PROFIT-LIVE-R39M_A7_120MIN_CAPTURE_GRADE_CHECK_NO_PATCH_NO_START_NO_STOP_NO_ORDER_verify_120min_continuity_safety_errors_feature_validity_candidate_blocker_surfaces_after_r39l_20260602_132654.md
docs/milestones/B1-PROFIT-LIVE-R39W4_LIVE_DECISION_BLOCKER_CONSUMER_VIEW_AUDIT_NO_PATCH_NO_START_NO_ORDER_ten_minute_read_only_decision_reason_candidate_blocker_safe_to_consume_payload_sync_audit_20260603_095554.md
docs/milestones/B1-PROFIT-LIVE-R39W5_CONSUMER_BRIDGE_EXACT_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_read_only_parse_decision_payload_source_bridge_leaf_invocation_candidate_export_seam_20260603_101233.md
docs/milestones/B1-PROFIT-LIVE-R39W8_NO_CANDIDATE_SCORE_GAP_BLOCKER_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_final_pobserve_candidate_absence_by_family_branch_score_gap_and_real_blocker_distribution_20260603_115326.md
docs/milestones/B1-PROFIT-LIVE-R39WA_VOLATILE_MARKET_ZERO_CANDIDATE_ROOT_CAUSE_NO_PATCH_NO_START_NO_ORDER_audit_raw_market_move_vs_feature_regime_score_response_for_zero_candidate_in_volatile_market_20260603_133915.md
docs/milestones/B1-PROFIT-LIVE-R3_CLASSIC_READY_BLOCKER_EXTRACTION_NO_ORDER_extract_why_provider_ready_classic_rows_still_no_candidate_no_patch_no_start_no_kill_no_delete_no_order_20260521_094952.md
docs/milestones/B1-PROFIT-LIVE-R6_CLASSIC_RUNTIME_ENABLEMENT_PATCH_PLAN_NO_PATCH_NO_ORDER_plan_narrow_observe_only_classic_runtime_candidate_enablement_after_r5_no_patch_no_start_no_order_20260521_100157.md
docs/milestones/B1-PROFIT-LIVE-R7-R9_APPROVAL_GATED_OBSERVE_ONLY_STRATEGY_RESTART_WITH_CLASSIC_RUNTIME_FLAG_NO_ORDER_restart_strategy_only_with_classic_runtime_observe_flag_verify_candidate_gate_no_risk_no_execution_no_order_20260521_111556.md
docs/milestones/B1-PROFIT-R0_PROFITABILITY_AND_DATA_SUFFICIENCY_AUDIT_NO_ORDER_audit_available_live_replay_candidate_and_decision_data_before_any_paper_trial_no_start_no_order_20260520_144425.md
docs/milestones/B1-PROFIT-R1_OPTION_CONTEXT_AND_CANDIDATE_GENERATION_BLOCKER_AUDIT_NO_ORDER_audit_dhan_option_context_provider_readiness_and_no_candidate_causes_no_patch_no_start_no_order_20260520_145726.md
docs/milestones/B1-PROFIT-R2_DHAN_OPTION_CONTEXT_RESTORE_OR_DEGRADE_ROUTE_PLAN_NO_ORDER_plan_restore_dhan_option_context_or_degraded_candidate_generation_route_no_patch_no_start_no_order_20260520_150536.md
docs/milestones/B1-PROFIT-SIM-R1_RECORDED_CANDIDATE_PNL_PRECHECK_NO_ORDER_after_market_precheck_candidate_pnl_files_from_recorded_inventory_no_start_no_order_20260520_232330.md
docs/milestones/B1-PROFIT-SIM-R2_RECORDED_PNL_SUMMARY_NO_ORDER_after_market_summarize_recorded_pnl_csvs_from_r1_precheck_no_start_no_order_20260520_232551.md
docs/milestones/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335.md
docs/milestones/B1-R26_EXECUTION_SHADOW_SEAM_AUDIT_NO_PATCH_NO_START_locate_execution_shadow_no_broker_seam_20260517_161940_milestone.md
docs/milestones/B1-R27_EXECUTION_SHADOW_BOOTSTRAP_ROUTE_PLAN_NO_PATCH_NO_START_map_existing_execution_shadow_bootstrap_route_20260517_162107_milestone.md
docs/milestones/B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START_bind_observe_only_execution_shadow_no_broker_route_20260517_162549_milestone.md
docs/milestones/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308.md
docs/milestones/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051.md
docs/milestones/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.md
docs/milestones/B1A-R38_LIFECYCLE_TRIGGER_PATCH_APPROVAL_REQUIRED_patch_observe_only_lifecycle_publishers_for_risk_execution_no_start_no_replay_no_pnl_20260517_171410.md
docs/milestones/B1A-R41_STATUS_ONLY_LIFECYCLE_ATTESTATION_FOR_B1B_NO_PATCH_NO_START_machine_readable_attestation_lifecycle_rows_status_only_for_b1b_r4d_no_replay_no_pnl_20260517_173407.md
docs/milestones/B1B-R4D_ACCEPT_B1A_STATUS_ONLY_ATTESTATION_RUNTIME_LIFECYCLE_ACCEPTED_NO_BACKTEST_NO_PNL_ingest_b1a_r41_attestation_accept_runtime_lifecycle_keep_backtest_not_admitted_pnl_not_ready_20260517_173549.md
docs/milestones/B1B-R5_BACKTEST_ADMISSION_REMAINS_NOT_ADMITTED_PENDING_VALID_TRADE_LIFECYCLE_freeze_runtime_lifecycle_accepted_but_backtest_pnl_blocked_until_valid_trade_lifecycle_no_patch_no_start_20260517_173722.md
docs/milestones/B3-R10_FIX_FEATURE_DECISION_DATASET_LAYOUT_NO_ORDER_stage_opt_ticks_required_and_features_decisions_optional_then_test_valid_replay_scopes_no_broker_order_pnl_20260521_125540.md
docs/milestones/B3-R11_ONE_STRATEGY_DETERMINISTIC_DRY_REPLAY_NO_ORDER_run_two_deterministic_feeds_features_strategy_dry_replays_for_mist_call_no_broker_order_pnl_20260521_133642.md
docs/milestones/B3-R1_LIVE_DATASET_ADMISSION_AUDIT_NO_START_NO_REPLAY_NO_ORDER_audit_existing_live_streams_for_replay_dataset_admission_without_start_stop_replay_order_pnl_20260521_101008.md
docs/milestones/B3-R20_REPLAYABLE_DATA_SOURCE_LOCATOR_NO_PATCH_NO_START_NO_ORDER_find_redis_or_disk_captured_dataset_candidates_after_r19_empty_redis_export_20260527_005409.md
docs/milestones/B3-R25A_REPLAY_ROW_SURFACE_DEEP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_strategy_decisions_features_rows_risk_execution_shadow_for_candidate_blocker_economics_fields_20260528_231726.md
docs/milestones/B3-R25_REPLAY_ARTIFACT_CONTENT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_r24g_replay_outputs_candidate_trade_economics_surfaces_20260528_231553.md
docs/milestones/B3-R28_REPLAY_ARTIFACT_FIELD_PATH_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_nested_field_paths_for_family_side_blocker_candidate_economics_in_replay_artifacts_20260531_192815.md
docs/milestones/B3-R29_REPLAY_EXPORT_SCHEMA_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_candidate_blocker_economics_family_side_export_schema_from_r28_field_paths_20260531_193156.md
docs/milestones/B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_exact_replay_artifact_writer_owner_for_candidate_blocker_economics_family_side_exports_20260531_193340.md
docs/milestones/B3-R31_REPLAY_EXPORT_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_exact_artifacts_py_patch_for_candidate_blocker_economics_family_side_exports_20260531_195140.md
docs/milestones/B3-R32_REPLAY_ANALYSIS_EXPORTS_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER_patch_artifacts_py_add_candidate_blocker_economics_family_side_exports_compile_only_20260531_210853.md
docs/milestones/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012.md
docs/milestones/B3-R39_REPLAY_EXPORT_CONTENT_REVIEW_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_summarize_candidate_blocker_economics_family_side_exports_from_r37_without_replay_or_patch_20260531_213316.md
docs/milestones/B3-R3_OFFLINE_REPLAY_DRY_RUN_FROM_CAPTURED_SURFACES_ZERODHA_ONLY_NO_BROKER_NO_ORDER_run_or_block_offline_replay_mvp_dry_run_from_b3_r2_manifest_without_broker_order_pnl_20260521_102211.md
docs/milestones/B3-R42_ECONOMICS_EXPORT_ENRICHMENT_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_review_r41_authority_candidates_and_freeze_safe_economics_summary_enrichment_design_20260531_214734.md
docs/milestones/B3-R43_ECONOMICS_SUMMARY_ENRICHMENT_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER_patch_artifacts_py_add_source_labelled_economics_summary_enrichment_compile_only_20260531_214953.md
docs/milestones/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243.md
docs/milestones/B3-R4_DETERMINISTIC_OFFLINE_REPLAY_EXECUTION_DRY_ONLY_NO_BROKER_NO_ORDER_run_deterministic_offline_replay_cli_dry_only_from_mvp_dataset_no_broker_order_pnl_20260521_102417.md
docs/milestones/B3-R54A_AGGREGATE_HELPER_CANDIDATE_FILE_LOCATOR_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_locate_r47_candidate_audit_file_and_explain_r54_zero_candidate_rows_20260531_231756.md
docs/milestones/B3-R55_AGGREGATE_HELPER_FILE_DISCOVERY_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_plan_fix_for_r53_helper_to_discover_candidate_audit_at_run_root_and_other_exports_in_artifacts_dir_20260531_232020.md
docs/milestones/B3-R56_AGGREGATE_HELPER_FILE_DISCOVERY_ONE_FILE_PATCH_NO_REDIS_NO_REPLAY_NO_ORDER_patch_artifacts_py_helper_to_find_candidate_audit_at_run_root_and_exports_in_artifacts_dir_20260531_232300.md
docs/milestones/B3-R57_AGGREGATE_HELPER_SMOKE_AFTER_R56_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_rerun_manual_helper_after_r56_verify_candidate_rows_and_combined_aggregate_counts_20260531_232628.md
docs/milestones/B3-R61B_A7_DURABLE_CAPTURE_REPLAY_CONSUMABILITY_NO_REDIS_NO_PATCH_NO_ORDER_build_dataset_from_r61a_confirmed_durable_fut_opt_run_replay_exports_candidate_blocker_economics_audit_20260602_221650.md
docs/milestones/B3-R61_A7_SEALED_DAY_REPLAY_CONSUMABILITY_AND_BLOCKER_AUDIT_NO_REDIS_NO_PATCH_NO_ORDER_build_replay_dataset_from_a7_pseal_run_offline_replay_exports_economics_candidate_blocker_analysis_20260602_220634.md
docs/milestones/B3-R62_DISTINCT_DAY_AGGREGATE_COMPARISON_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_combine_20260527_and_20260602_replay_runs_with_manual_aggregate_helper_and_compare_candidate_blocker_economics_20260602_223148.md
docs/milestones/B3-R9_ONE_STRATEGY_DRY_REPLAY_COMPATIBILITY_CHECK_NO_ORDER_check_replay_cli_strategy_stage_compatibility_using_b3_r8_mist_call_adapter_no_broker_order_pnl_20260521_125333.md
docs/milestones/B4-DAY3-R3_OFFLINE_STRATEGY_QUALIFICATION_FORENSIC_MAP_NO_PATCH_NO_START_NO_ORDER_map_activation_no_candidate_nearest_miss_score_regime_breakout_confirmation_and_selected_option_side_seams_20260603_222012.md
docs/milestones/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351.md
docs/milestones/LANE-F-R0_VALID_TRADE_LIFECYCLE_EVIDENCE_INVENTORY_NO_PATCH_NO_START_read_only_inventory_for_valid_trade_lifecycle_data_after_b1b_r5_wait_state_no_replay_no_pnl_20260517_173947.md
docs/milestones/LANE-F-R1_VALIDATE_CANDIDATE_LIFECYCLE_FILES_NO_REPLAY_NO_PNL_read_only_validate_possible_lifecycle_candidate_files_from_lane_f_r0_no_admission_no_replay_no_pnl_20260517_174249.md
docs/milestones/LANE-F-R2_CAPTURE_PLAN_FOR_FUTURE_VALID_TRADE_LIFECYCLE_DATA_NO_START_freeze_future_live_session_valid_trade_lifecycle_capture_plan_no_patch_no_start_no_replay_no_pnl_20260517_174422.md
docs/milestones/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607.md
docs/milestones/LANE-F-R4R12_DIAGNOSTIC_PATCH_STATIC_PROOF_NO_START_static_verify_r4r11r_diagnostic_helpers_compile_zero_order_no_start_no_replay_no_pnl_20260518_152329.md
docs/milestones/LANE-F-R4R13R2_TINY_LIVE_DECISION_DIAGNOSTIC_CAPTURE_NO_ORDER_tiny_recovery_capture_current_decision_diagnostic_fields_no_start_no_replay_no_pnl_20260519_102918.md
docs/milestones/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156.md
docs/milestones/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619.md
docs/milestones/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219.md
docs/milestones/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909.md
docs/milestones/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548.md
docs/milestones/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917.md
docs/milestones/LANE-F-R4R15H_RAW_MERGE_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_activation_raw_merge_runtime_diagnostics_no_start_no_replay_no_pnl_no_order_20260519_224247.md
docs/milestones/LANE-F-R4R15_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_runtime_gate_diagnostics_into_strategy_decision_output_only_no_start_no_replay_no_pnl_no_order_20260519_103327.md
docs/milestones/LANE-F-R4R16_RAW_MERGE_WIRING_STATIC_PROOF_NO_START_static_verify_r4r15h_raw_merge_patch_compile_zero_order_no_start_no_replay_no_pnl_20260519_224330.md
docs/milestones/LANE-F-R4R17A_OBSERVE_ONLY_STRATEGY_RESTART_DECISION_REQUIRED_NO_ORDER_decide_next_live_session_observe_only_restart_needed_for_raw_diagnostic_visibility_no_start_no_replay_no_pnl_20260519_225039.md
docs/milestones/LANE-F-R4R17R_TAIL_DECISION_DIAGNOSTIC_VISIBILITY_CAPTURE_NO_ORDER_recover_r4r17_with_tail_based_decision_capture_no_xread_no_start_no_replay_no_pnl_20260519_224820.md
docs/milestones/LANE-F-R4R18AR_RECOVER_AFTERMARKET_HANDOFF_BUNDLE_NO_START_recover_archive_packaging_after_relative_path_error_no_start_no_replay_no_pnl_20260519_231123.md
docs/milestones/LANE-F-R4R18A_AFTERMARKET_RAW_DIAGNOSTIC_PATCH_HANDOFF_BUNDLE_NO_START_compact_bundle_raw_diagnostic_patch_evidence_next_live_session_no_start_no_replay_no_pnl_20260519_230750.md
docs/milestones/LANE-F-R4R18B_ORPHAN_MAIN_PROCESS_CLASSIFICATION_NO_START_classify_generic_main_process_after_r4r18_preflight_no_start_no_order_no_replay_no_pnl_20260520_093120.md
docs/milestones/LANE-F-R4R18_OBSERVE_ONLY_STACK_RESTART_PREFLIGHT_NO_START_live_session_preflight_before_observe_only_feeds_features_strategy_restart_no_order_no_replay_no_pnl_20260520_092948.md
docs/milestones/LANE-F-R4R19H5_APPROVED_INSTRUMENT_METADATA_REFRESH_NO_ORDER_NO_REPLAY_approved_refresh_nfo_instrument_metadata_after_feeds_stale_failure_no_order_no_replay_no_pnl_20260520_100348.md
docs/milestones/LANE-F-R4R4_DECISION_TAIL_AUDIT_AFTER_NO_LIFECYCLE_NO_PATCH_NO_START_read_only_audit_latest_decisions_after_live_capture_no_candidate_no_replay_no_pnl_20260518_143451.md
docs/milestones/LANE-F-R4R5_STRATEGY_BLOCKER_AUDIT_NO_PATCH_NO_START_read_only_audit_strategy_blockers_after_no_candidate_decisions_no_replay_no_pnl_20260518_143812.md
docs/milestones/LANE-F-R4R6_DATA_QUALITY_BLOCKER_AUDIT_NO_PATCH_NO_START_read_only_audit_stage_data_quality_ok_failed_from_live_features_decisions_no_replay_no_pnl_20260518_144017.md
docs/milestones/LANE-F-R4R7_RUNTIME_ENABLEMENT_SURFACE_AUDIT_NO_PATCH_NO_START_read_only_audit_why_classic_and_miso_runtime_disabled_no_order_no_replay_no_pnl_20260518_144147.md
docs/milestones/LANE-F-R4R8R2_RUNTIME_GATE_MINIMAL_PATCH_PLAN_NO_PATCH_NO_START_minimal_recovery_plan_after_broken_paste_no_live_change_no_replay_no_pnl_20260518_144956.md
docs/milestones/LANE-F-R4R9R_SOURCE_REVIEW_RECOVERY_NO_PATCH_NO_START_compact_runtime_gate_source_review_after_broken_paste_no_replay_no_pnl_20260518_145356.md
docs/milestones/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712.md
docs/milestones/LANE-X-R24B_shadow_near_candidate_observer_helper_no_production_candidate_no_order_20260604_230313.md
docs/milestones/LANE-X-R24C_post_r24b_shadow_near_candidate_finalizer_no_patch_no_order_20260604_230456.md
docs/milestones/LANE-X-R25O_candidate_promotion_gap_inspector_no_patch_no_order_20260605_110846.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_190621.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_190624.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_191629.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_191836.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_192108.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_192310.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_192948.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_193556.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_193557.md
docs/milestones/batch_raw_aa10_r1_guarded_candidate_execution_20260501_194228.md
docs/milestones/batch_raw_aa14_pnl_cost_model_source_resolver_20260502_112226.md
docs/milestones/batch_raw_aa14_pnl_cost_model_source_resolver_20260502_112815.md
docs/milestones/batch_raw_aa17_r2_trade_lifecycle_pnl_authority_resolver_20260502_125729.md
docs/milestones/batch_raw_aa3_canonical_trade_pnl_ranking_20260501_180316.md
docs/milestones/batch_raw_aa7_bounded_candidate_generation_preflight_20260501_184042.md
docs/milestones/batch_raw_aa8_bounded_candidate_execution_command_construction_20260501_190008.md
docs/milestones/batch_raw_aa9_guarded_candidate_execution_readiness_review_20260501_190211.md
docs/milestones/batch_raw_e_pnl_analytics_freeze_final_20260501_130154.md
docs/milestones/batch_raw_q_trade_family_backfill_freeze_final_20260501_143325.md
docs/milestones/batch_raw_r_family_pnl_gap_review_freeze_final_20260501_143807.md
docs/milestones/lane_a5b_r1c_focused_a4_readiness_candidate_normalization_20260511_120118.md
docs/milestones/lane_d1_d41_candidate_subset_selection_20260510_220657.md
docs/milestones/lane_d2_d41_lane_e_candidate_materialization_intake_20260510_222235.md
docs/milestones/lane_d_d20_candidate_trade_matching_schema_20260510_200738.md
docs/milestones/lane_d_d21_candidate_trade_readiness_20260510_200931.md
docs/milestones/lane_d_d25_candidate_context_enrichment_20260510_205442.md
docs/milestones/lane_d_d29_candidate_result_bridge_20260510_210324.md
docs/milestones/lane_d_d30_candidate_context_value_source_20260510_210558.md
docs/milestones/lane_d_d31_candidate_replay_binding_requirement_20260510_211039.md
docs/milestones/lane_d_d32_candidate_replay_binding_plan_20260510_211204.md
docs/milestones/lane_d_d33_candidate_replay_binding_plan_validator_20260510_211334.md
docs/milestones/lane_d_d34_candidate_replay_materialization_20260510_211554.md
docs/milestones/lane_d_d35_candidate_replay_materialization_validator_20260510_211903.md
docs/milestones/lane_d_d36_candidate_replay_materialization_preflight_20260510_212255.md
docs/milestones/lane_d_d5_candidate_matrix_20260510_191240.md
docs/milestones/replay_data_a14_execution_shadow_20260508T184414Z.md
docs/milestones/replay_data_a14_execution_shadow_20260508T184835Z.md
docs/milestones/replay_data_a18_execution_shadow_semantic_normalization_20260508T191103Z.md
docs/milestones/replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.md
docs/milestones/replay_data_a65_r2_integrity_stem_equivalence_execution_shadow_precheck_20260510T142256Z.md
docs/milestones/replay_data_a66_execution_shadow_durable_start_20260510T142418Z.md
docs/milestones/replay_data_a67_post_execution_shadow_audit_next_scope_precheck_20260510T142850Z.md
docs/milestones/replay_data_a72_candidate_trade_fill_dataset_discovery_20260510T152306Z.md
docs/milestones/replay_data_a73_r2_alternate_fill_dataset_scan_20260510T152746Z.md
docs/milestones/replay_data_a75_fill_dataset_build_route_audit_20260510T153619Z.md
docs/milestones/replay_data_a76_fill_build_contract_guarded_plan_20260510T153802Z.md
docs/milestones/replay_data_a77_guarded_offline_simulated_fill_builder_20260510T154027Z.md
docs/milestones/replay_data_a78_simulated_fill_dataset_admission_gate_20260510T154221Z.md
docs/runbooks/A6-PAPER-AFTERMARKET-R18-R3_short_read_only_latest_stream_pfeeds_pstack_candidate_audit_no_start_no_order_no_paper_20260520_000533_runbook.md
docs/runbooks/A6-PAPER-AFTERMARKET-R18_pfeeds_pstack_backtest_data_and_strategy_candidate_audit_no_start_no_order_no_paper_20260520_000152_runbook.md
docs/runbooks/A6-PAPER-R17M-R2B_pfeeds_pstack_readiness_and_candidate_audit_after_r17m_r2_block_no_risk_no_execution_no_order_20260520_094641_runbook.md
docs/runbooks/A6-PAPER-R17M-R2J_read_only_running_stack_lock_owner_and_candidate_ratification_after_r2i_no_start_no_kill_no_delete_no_order_20260520_101536_runbook.md
docs/runbooks/A6-PAPER-R17O-R1_fresh_live_candidate_scope_audit_rerun_no_start_no_order_no_enablement_20260520_110014_candidate_scope_audit.md
docs/runbooks/A6-PAPER-R17O-R2_extended_fresh_live_candidate_watch_no_start_no_order_no_enablement_20260520_130111_candidate_watch.md
docs/runbooks/A6-PAPER-R17O-R2_extended_fresh_live_candidate_watch_no_start_no_order_no_enablement_20260520_130526_candidate_watch.md
docs/runbooks/A6-PAPER-R17O-R3_candidate_absence_forensics_from_live_decisions_no_start_no_order_no_enablement_20260520_131223_candidate_absence_forensics.md
docs/runbooks/A6-PAPER-R17O-R4_fresh_candidate_audit_after_strategy_decision_recovery_with_diagnostic_limitation_no_start_no_order_20260520_144126_candidate_audit.md
docs/runbooks/A6-PAPER-R17O_fresh_live_candidate_scope_audit_before_any_paper_order_no_start_no_order_no_enablement_20260520_105628_candidate_scope_audit.md
docs/runbooks/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_dedicated_dhan_context_service_design.md
docs/runbooks/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_next_route_runbook.md
docs/runbooks/B1-PROFIT-CLASSIC-R0_CLASSIC_READY_NO_CANDIDATE_ROOT_CAUSE_AUDIT_NO_ORDER_after_market_audit_classic_ready_decisions_why_no_mist_misb_misc_misr_candidate_no_start_no_order_20260520_231628_next_route_runbook.md
docs/runbooks/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701_next_day_plan.md
docs/runbooks/B1-PROFIT-LIVE-R0_CLASSIC_CANDIDATE_AND_DHAN_CONTEXT_GROWTH_AUDIT_NO_ORDER_live_session_audit_pfeeds_pstack_dhan_context_classic_candidate_growth_no_patch_no_start_no_order_20260521_094211_next_route_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R1_LOCK_PROCESS_AND_CLASSIC_READY_NO_CANDIDATE_TRIAGE_NO_ORDER_read_only_triage_execution_lock_service_detection_and_classic_ready_zero_candidate_no_start_no_kill_no_delete_no_order_20260521_094428_next_route_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R38F_live_observe_only_fallback_candidate_surface_preflight_no_paper_no_order_20260529_094258_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R38X-R2_strict_json_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_195424_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R38X_offline_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_194922_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R38ZH-R2_offline_patched_candidate_reevaluation_after_stale_feed_cleanup_no_patch_no_order_20260531_225914_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R39W4_LIVE_DECISION_BLOCKER_CONSUMER_VIEW_AUDIT_NO_PATCH_NO_START_NO_ORDER_ten_minute_read_only_decision_reason_candidate_blocker_safe_to_consume_payload_sync_audit_20260603_095554_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R39W5_CONSUMER_BRIDGE_EXACT_SEAM_AUDIT_NO_PATCH_NO_START_NO_ORDER_read_only_parse_decision_payload_source_bridge_leaf_invocation_candidate_export_seam_20260603_101233_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R39W8_NO_CANDIDATE_SCORE_GAP_BLOCKER_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_final_pobserve_candidate_absence_by_family_branch_score_gap_and_real_blocker_distribution_20260603_115326_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R39W9_CANDIDATE_TRIGGER_WATCH_NO_PATCH_NO_START_NO_ORDER_watch_live_decisions_for_candidate_positive_or_near_candidate_score_gap_without_paper_20260603_121513_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R39WA_VOLATILE_MARKET_ZERO_CANDIDATE_ROOT_CAUSE_NO_PATCH_NO_START_NO_ORDER_audit_raw_market_move_vs_feature_regime_score_response_for_zero_candidate_in_volatile_market_20260603_133915_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R3_CLASSIC_READY_BLOCKER_EXTRACTION_NO_ORDER_extract_why_provider_ready_classic_rows_still_no_candidate_no_patch_no_start_no_kill_no_delete_no_order_20260521_094952_next_route_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R6_CLASSIC_RUNTIME_ENABLEMENT_PATCH_PLAN_NO_PATCH_NO_ORDER_plan_narrow_observe_only_classic_runtime_candidate_enablement_after_r5_no_patch_no_start_no_order_20260521_100157_next_route_runbook.md
docs/runbooks/B1-PROFIT-LIVE-R7-R9_APPROVAL_GATED_OBSERVE_ONLY_STRATEGY_RESTART_WITH_CLASSIC_RUNTIME_FLAG_NO_ORDER_restart_strategy_only_with_classic_runtime_observe_flag_verify_candidate_gate_no_risk_no_execution_no_order_20260521_111556_next_route_runbook.md
docs/runbooks/B1-PROFIT-R0_PROFITABILITY_AND_DATA_SUFFICIENCY_AUDIT_NO_ORDER_audit_available_live_replay_candidate_and_decision_data_before_any_paper_trial_no_start_no_order_20260520_144425_next_route_runbook.md
docs/runbooks/B1-PROFIT-R1_OPTION_CONTEXT_AND_CANDIDATE_GENERATION_BLOCKER_AUDIT_NO_ORDER_audit_dhan_option_context_provider_readiness_and_no_candidate_causes_no_patch_no_start_no_order_20260520_145726_next_route_runbook.md
docs/runbooks/B1-PROFIT-R2_DHAN_OPTION_CONTEXT_RESTORE_OR_DEGRADE_ROUTE_PLAN_NO_ORDER_plan_restore_dhan_option_context_or_degraded_candidate_generation_route_no_patch_no_start_no_order_20260520_150536_next_route_runbook.md
docs/runbooks/B1-PROFIT-SIM-R1_RECORDED_CANDIDATE_PNL_PRECHECK_NO_ORDER_after_market_precheck_candidate_pnl_files_from_recorded_inventory_no_start_no_order_20260520_232330_next_route_runbook.md
docs/runbooks/B1-PROFIT-SIM-R2_RECORDED_PNL_SUMMARY_NO_ORDER_after_market_summarize_recorded_pnl_csvs_from_r1_precheck_no_start_no_order_20260520_232551_next_route_runbook.md
docs/runbooks/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335_next_route_runbook.md
docs/runbooks/B1-R26_EXECUTION_SHADOW_SEAM_AUDIT_NO_PATCH_NO_START_locate_execution_shadow_no_broker_seam_20260517_161940_runbook.md
docs/runbooks/B1-R27_EXECUTION_SHADOW_BOOTSTRAP_ROUTE_PLAN_NO_PATCH_NO_START_map_existing_execution_shadow_bootstrap_route_20260517_162107_runbook.md
docs/runbooks/B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START_bind_observe_only_execution_shadow_no_broker_route_20260517_162549_runbook.md
docs/runbooks/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308_next_route_runbook.md
docs/runbooks/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_next_execute_runbook.md
docs/runbooks/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_next_execute_runbook.md
docs/runbooks/B1A-R38_LIFECYCLE_TRIGGER_PATCH_APPROVAL_REQUIRED_patch_observe_only_lifecycle_publishers_for_risk_execution_no_start_no_replay_no_pnl_20260517_171410_next_execute_runbook.md
docs/runbooks/B1A-R41_STATUS_ONLY_LIFECYCLE_ATTESTATION_FOR_B1B_NO_PATCH_NO_START_machine_readable_attestation_lifecycle_rows_status_only_for_b1b_r4d_no_replay_no_pnl_20260517_173407_b1b_r4d_next_route_runbook.md
docs/runbooks/B1B-R4D_ACCEPT_B1A_STATUS_ONLY_ATTESTATION_RUNTIME_LIFECYCLE_ACCEPTED_NO_BACKTEST_NO_PNL_ingest_b1a_r41_attestation_accept_runtime_lifecycle_keep_backtest_not_admitted_pnl_not_ready_20260517_173549_next_route_runbook.md
docs/runbooks/B1B-R5_BACKTEST_ADMISSION_REMAINS_NOT_ADMITTED_PENDING_VALID_TRADE_LIFECYCLE_freeze_runtime_lifecycle_accepted_but_backtest_pnl_blocked_until_valid_trade_lifecycle_no_patch_no_start_20260517_173722_next_route_runbook.md
docs/runbooks/B3-R10_FIX_FEATURE_DECISION_DATASET_LAYOUT_NO_ORDER_stage_opt_ticks_required_and_features_decisions_optional_then_test_valid_replay_scopes_no_broker_order_pnl_20260521_125540_next_route_runbook.md
docs/runbooks/B3-R11_ONE_STRATEGY_DETERMINISTIC_DRY_REPLAY_NO_ORDER_run_two_deterministic_feeds_features_strategy_dry_replays_for_mist_call_no_broker_order_pnl_20260521_133642_next_route_runbook.md
docs/runbooks/B3-R1_LIVE_DATASET_ADMISSION_AUDIT_NO_START_NO_REPLAY_NO_ORDER_audit_existing_live_streams_for_replay_dataset_admission_without_start_stop_replay_order_pnl_20260521_101008_next_route_runbook.md
docs/runbooks/B3-R20_REPLAYABLE_DATA_SOURCE_LOCATOR_NO_PATCH_NO_START_NO_ORDER_find_redis_or_disk_captured_dataset_candidates_after_r19_empty_redis_export_20260527_005409_next_route_runbook.md
docs/runbooks/B3-R25A_REPLAY_ROW_SURFACE_DEEP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_strategy_decisions_features_rows_risk_execution_shadow_for_candidate_blocker_economics_fields_20260528_231726_next_route_runbook.md
docs/runbooks/B3-R25_REPLAY_ARTIFACT_CONTENT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_r24g_replay_outputs_candidate_trade_economics_surfaces_20260528_231553_next_route_runbook.md
docs/runbooks/B3-R28_REPLAY_ARTIFACT_FIELD_PATH_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_nested_field_paths_for_family_side_blocker_candidate_economics_in_replay_artifacts_20260531_192815_next_route_runbook.md
docs/runbooks/B3-R29_REPLAY_EXPORT_SCHEMA_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_candidate_blocker_economics_family_side_export_schema_from_r28_field_paths_20260531_193156_next_route_runbook.md
docs/runbooks/B3-R30_REPLAY_EXPORT_WRITER_SOURCE_OWNERSHIP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_exact_replay_artifact_writer_owner_for_candidate_blocker_economics_family_side_exports_20260531_193340_next_route_runbook.md
docs/runbooks/B3-R31_REPLAY_EXPORT_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_exact_artifacts_py_patch_for_candidate_blocker_economics_family_side_exports_20260531_195140_next_route_runbook.md
docs/runbooks/B3-R32_REPLAY_ANALYSIS_EXPORTS_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER_patch_artifacts_py_add_candidate_blocker_economics_family_side_exports_compile_only_20260531_210853_next_route_runbook.md
docs/runbooks/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_next_route_runbook.md
docs/runbooks/B3-R39_REPLAY_EXPORT_CONTENT_REVIEW_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_summarize_candidate_blocker_economics_family_side_exports_from_r37_without_replay_or_patch_20260531_213316_next_route_runbook.md
docs/runbooks/B3-R3_OFFLINE_REPLAY_DRY_RUN_FROM_CAPTURED_SURFACES_ZERODHA_ONLY_NO_BROKER_NO_ORDER_run_or_block_offline_replay_mvp_dry_run_from_b3_r2_manifest_without_broker_order_pnl_20260521_102211_next_route_runbook.md
docs/runbooks/B3-R42_ECONOMICS_EXPORT_ENRICHMENT_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_review_r41_authority_candidates_and_freeze_safe_economics_summary_enrichment_design_20260531_214734_next_route_runbook.md
docs/runbooks/B3-R43_ECONOMICS_SUMMARY_ENRICHMENT_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER_patch_artifacts_py_add_source_labelled_economics_summary_enrichment_compile_only_20260531_214953_next_route_runbook.md
docs/runbooks/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_next_route_runbook.md
docs/runbooks/B3-R4_DETERMINISTIC_OFFLINE_REPLAY_EXECUTION_DRY_ONLY_NO_BROKER_NO_ORDER_run_deterministic_offline_replay_cli_dry_only_from_mvp_dataset_no_broker_order_pnl_20260521_102417_next_route_runbook.md
docs/runbooks/B3-R54A_AGGREGATE_HELPER_CANDIDATE_FILE_LOCATOR_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_locate_r47_candidate_audit_file_and_explain_r54_zero_candidate_rows_20260531_231756_next_route_runbook.md
docs/runbooks/B3-R55_AGGREGATE_HELPER_FILE_DISCOVERY_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_plan_fix_for_r53_helper_to_discover_candidate_audit_at_run_root_and_other_exports_in_artifacts_dir_20260531_232020_next_route_runbook.md
docs/runbooks/B3-R56_AGGREGATE_HELPER_FILE_DISCOVERY_ONE_FILE_PATCH_NO_REDIS_NO_REPLAY_NO_ORDER_patch_artifacts_py_helper_to_find_candidate_audit_at_run_root_and_exports_in_artifacts_dir_20260531_232300_next_route_runbook.md
docs/runbooks/B3-R57_AGGREGATE_HELPER_SMOKE_AFTER_R56_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_rerun_manual_helper_after_r56_verify_candidate_rows_and_combined_aggregate_counts_20260531_232628_next_route_runbook.md
docs/runbooks/B3-R61B_A7_DURABLE_CAPTURE_REPLAY_CONSUMABILITY_NO_REDIS_NO_PATCH_NO_ORDER_build_dataset_from_r61a_confirmed_durable_fut_opt_run_replay_exports_candidate_blocker_economics_audit_20260602_221650_next_route_runbook.md
docs/runbooks/B3-R61_A7_SEALED_DAY_REPLAY_CONSUMABILITY_AND_BLOCKER_AUDIT_NO_REDIS_NO_PATCH_NO_ORDER_build_replay_dataset_from_a7_pseal_run_offline_replay_exports_economics_candidate_blocker_analysis_20260602_220634_next_route_runbook.md
docs/runbooks/B3-R62_DISTINCT_DAY_AGGREGATE_COMPARISON_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_combine_20260527_and_20260602_replay_runs_with_manual_aggregate_helper_and_compare_candidate_blocker_economics_20260602_223148_next_route_runbook.md
docs/runbooks/B3-R9_ONE_STRATEGY_DRY_REPLAY_COMPATIBILITY_CHECK_NO_ORDER_check_replay_cli_strategy_stage_compatibility_using_b3_r8_mist_call_adapter_no_broker_order_pnl_20260521_125333_next_route_runbook.md
docs/runbooks/B4-DAY3-R3_OFFLINE_STRATEGY_QUALIFICATION_FORENSIC_MAP_NO_PATCH_NO_START_NO_ORDER_map_activation_no_candidate_nearest_miss_score_regime_breakout_confirmation_and_selected_option_side_seams_20260603_222012_runbook.md
docs/runbooks/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_runbook.md
docs/runbooks/LANE-F-R0_VALID_TRADE_LIFECYCLE_EVIDENCE_INVENTORY_NO_PATCH_NO_START_read_only_inventory_for_valid_trade_lifecycle_data_after_b1b_r5_wait_state_no_replay_no_pnl_20260517_173947_next_route_runbook.md
docs/runbooks/LANE-F-R1_VALIDATE_CANDIDATE_LIFECYCLE_FILES_NO_REPLAY_NO_PNL_read_only_validate_possible_lifecycle_candidate_files_from_lane_f_r0_no_admission_no_replay_no_pnl_20260517_174249_next_route_runbook.md
docs/runbooks/LANE-F-R2_CAPTURE_PLAN_FOR_FUTURE_VALID_TRADE_LIFECYCLE_DATA_NO_START_freeze_future_live_session_valid_trade_lifecycle_capture_plan_no_patch_no_start_no_replay_no_pnl_20260517_174422_future_live_session_runbook.md
docs/runbooks/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607_next_route_runbook.md
docs/runbooks/LANE-F-R4R12_DIAGNOSTIC_PATCH_STATIC_PROOF_NO_START_static_verify_r4r11r_diagnostic_helpers_compile_zero_order_no_start_no_replay_no_pnl_20260518_152329_next_route_runbook.md
docs/runbooks/LANE-F-R4R13R2_TINY_LIVE_DECISION_DIAGNOSTIC_CAPTURE_NO_ORDER_tiny_recovery_capture_current_decision_diagnostic_fields_no_start_no_replay_no_pnl_20260519_102918_next_route_runbook.md
docs/runbooks/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156_next_route_runbook.md
docs/runbooks/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619_next_route_runbook.md
docs/runbooks/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219_next_route_runbook.md
docs/runbooks/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909_next_route_runbook.md
docs/runbooks/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548_next_route_runbook.md
docs/runbooks/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917_next_route_runbook.md
docs/runbooks/LANE-F-R4R15H_RAW_MERGE_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_activation_raw_merge_runtime_diagnostics_no_start_no_replay_no_pnl_no_order_20260519_224247_next_route_runbook.md
docs/runbooks/LANE-F-R4R15_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_runtime_gate_diagnostics_into_strategy_decision_output_only_no_start_no_replay_no_pnl_no_order_20260519_103327_next_route_runbook.md
docs/runbooks/LANE-F-R4R16_RAW_MERGE_WIRING_STATIC_PROOF_NO_START_static_verify_r4r15h_raw_merge_patch_compile_zero_order_no_start_no_replay_no_pnl_20260519_224330_next_route_runbook.md
docs/runbooks/LANE-F-R4R17A_OBSERVE_ONLY_STRATEGY_RESTART_DECISION_REQUIRED_NO_ORDER_decide_next_live_session_observe_only_restart_needed_for_raw_diagnostic_visibility_no_start_no_replay_no_pnl_20260519_225039_next_live_session_runbook.md
docs/runbooks/LANE-F-R4R17R_TAIL_DECISION_DIAGNOSTIC_VISIBILITY_CAPTURE_NO_ORDER_recover_r4r17_with_tail_based_decision_capture_no_xread_no_start_no_replay_no_pnl_20260519_224820_next_route_runbook.md
docs/runbooks/LANE-F-R4R18AR_RECOVER_AFTERMARKET_HANDOFF_BUNDLE_NO_START_recover_archive_packaging_after_relative_path_error_no_start_no_replay_no_pnl_20260519_231123_next_live_session_r4r18_runbook.md
docs/runbooks/LANE-F-R4R18A_AFTERMARKET_RAW_DIAGNOSTIC_PATCH_HANDOFF_BUNDLE_NO_START_compact_bundle_raw_diagnostic_patch_evidence_next_live_session_no_start_no_replay_no_pnl_20260519_230750_next_live_session_r4r18_runbook.md
docs/runbooks/LANE-F-R4R18B_ORPHAN_MAIN_PROCESS_CLASSIFICATION_NO_START_classify_generic_main_process_after_r4r18_preflight_no_start_no_order_no_replay_no_pnl_20260520_093120_next_route_runbook.md

## Lane X / patch-impact clues as replay-validation context only
docs/milestones/2026-05-08_BATCH30J_R5P_REAL_INTEGRITY_CHECK_IMPLEMENTATION_PLAN.md
docs/milestones/A6-FEED-R5P_read_only_decisions_producer_blocker_inspection_after_expected_a6_dirty_state_no_patch_no_restore_no_restart_no_order_no_paper_20260514_134031.md
docs/milestones/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756.md
docs/milestones/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931.md
docs/milestones/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603.md
docs/milestones/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709.md
docs/milestones/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017.md
docs/milestones/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305.md
docs/milestones/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945.md
docs/milestones/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351.md
docs/milestones/B4-R5P-V1_MICRO_SHELF_PATCH_VERIFY_FINALIZE_NO_START_NO_ORDER_20260603_234959.md
docs/milestones/B4-R5P-V2_MICRO_SHELF_CONTRACT_PASSTHROUGH_SELFTEST_NO_START_NO_ORDER_20260603_235105.md
docs/milestones/B4-R5P-V3_MISB_SHELF_CONSUMER_SELFTEST_NO_START_NO_ORDER_20260603_235205.md
docs/milestones/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657.md
docs/runbooks/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_runbook.md
docs/runbooks/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_runbook.md
docs/runbooks/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_runbook.md
docs/runbooks/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_runbook.md
docs/runbooks/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_runbook.md
docs/runbooks/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305_runbook.md
docs/runbooks/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945_runbook.md
docs/runbooks/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_runbook.md
docs/runbooks/BATCH30J_R5P_REAL_INTEGRITY_CHECK_IMPLEMENTATION_PLAN_RUNBOOK.md
run/audits/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_raw/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_misb_formula_reproducer.json
run/audits/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_raw/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_raw.txt
run/audits/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_raw/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_source_extract.txt
run/audits/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_report.md
run/audits/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_raw/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_compute_score_exact_formula.json
run/audits/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_raw/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_exact_source_snippets.txt
run/audits/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_raw/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_raw.txt
run/audits/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_report.md
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_raw/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_misb_call_surface_breakout_lineage.json
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_raw/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_raw.txt
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_raw/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_source_snippets.txt
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_report.md
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_raw/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_misb_call_surface_breakout_lineage.json
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_raw/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_raw.txt
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_raw/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_source_snippets.txt
run/audits/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_report.md
run/audits/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_raw/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_provider_not_ready_lineage.json
run/audits/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_raw/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_raw.txt
run/audits/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_raw/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_source_snippets.txt
run/audits/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_report.md
run/audits/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305_raw/raw.txt
run/audits/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305_raw/shelf_extract.json
run/audits/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305_report.md
run/audits/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945_raw/raw.txt
run/audits/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945_raw/shelf_reason.json
run/audits/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945_report.md
run/audits/B4-DAY3-R5L_MICRO_SHELF_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_freeze_misb_micro_shelf_design_after_missing_explicit_shelf_proof_20260603_232505_raw.txt
run/audits/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_raw/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_raw.txt
run/audits/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_raw/evidence_hits.txt
run/audits/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_raw/score_decomposition_summary.json
run/audits/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_raw/source_hits.txt
run/audits/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_raw/source_snippets.txt
run/audits/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_report.md
run/audits/B4-R5P-V1_MICRO_SHELF_PATCH_VERIFY_FINALIZE_NO_START_NO_ORDER_20260603_234959_raw.txt
run/audits/B4-R5P-V2_MICRO_SHELF_CONTRACT_PASSTHROUGH_SELFTEST_NO_START_NO_ORDER_20260603_235105_raw.txt
run/audits/B4-R5P-V3_MISB_SHELF_CONSUMER_SELFTEST_NO_START_NO_ORDER_20260603_235205_raw.txt
run/audits/B4-R5P_MICRO_SHELF_PRODUCER_PATCH_NO_START_NO_ORDER_20260603_234829_raw.txt
run/audits/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657_raw.txt
run/audits/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657_report.md
run/proofs/A6-FEED-R5P_read_only_decisions_producer_blocker_inspection_after_expected_a6_dirty_state_no_patch_no_restore_no_restart_no_order_no_paper_20260514_134031.json
run/proofs/A6-FEED-R5P_read_only_decisions_producer_blocker_inspection_after_expected_a6_dirty_state_no_patch_no_restore_no_restart_no_order_no_paper_20260514_134031.json.sha256
run/proofs/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756.json
run/proofs/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931.json
run/proofs/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603.json
run/proofs/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709.json
run/proofs/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017.json
run/proofs/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305.json
run/proofs/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945.json
run/proofs/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351.json
run/proofs/B4-R5P-V1_MICRO_SHELF_PATCH_VERIFY_FINALIZE_NO_START_NO_ORDER_20260603_234959.json
run/proofs/B4-R5P-V2_MICRO_SHELF_CONTRACT_PASSTHROUGH_SELFTEST_NO_START_NO_ORDER_20260603_235105.json
run/proofs/B4-R5P-V3_MISB_SHELF_CONSUMER_SELFTEST_NO_START_NO_ORDER_20260603_235205.json
run/proofs/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/bin/proof_replay_baseline_shadow_comparison.py
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/bin/proof_replay_baseline_shadow_comparison.py
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_n_enriched_rerun_freeze_final_20260501_140812_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_n_enriched_rerun_freeze_final_20260501_140812_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_n_enriched_rerun_freeze_final_20260501_140812_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_n_enriched_rerun_freeze_final_20260501_140812_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/final_freeze_bundle_20260425_130932/artifacts/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/final_freeze_bundle_20260425_132522/artifacts/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/final_freeze_bundle_20260425_132522/artifacts/run/proofs/final_freeze_bundle_20260425_130932/artifacts/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/proof_replay_baseline_shadow_comparison.json
run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_c_module_skeleton_freeze_final_20260501_124832_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_d_dataset_quality_freeze_final_20260501_125325_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_e_pnl_analytics_freeze_final_20260501_130154_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_f_strategy_ranking_freeze_final_20260501_130542_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_g_oi_wall_impact_freeze_final_20260501_130854_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_h_forensics_freeze_final_20260501_131236_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_j_promotion_firewall_freeze_final_20260501_132028_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132327_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132409_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132409_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132409_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/02_decision_impact_summary.txt
run/proofs/batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132409_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/03_operator_readout.txt
run/proofs/batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/00_study_brief.txt
run/proofs/batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703_inspection/extracted_bundle/run/proofs/decision_impact_baseline15_vs_shadow12_2026-04-17/01_decision_impact_summary.json

## Route classification
CLASSIFICATION=PASS_R5_NO_EXISTING_FILL_RUN_FOUND_ROUTE_TO_PATCH_IMPACT_OR_FUTURE_VALID_TRADE_DATASET
