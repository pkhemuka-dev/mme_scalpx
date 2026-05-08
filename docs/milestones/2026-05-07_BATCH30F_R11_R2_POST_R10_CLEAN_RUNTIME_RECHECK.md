# Batch 30F-R11-R2 — Post-R10 Clean Runtime Recheck

Verdict: PASS_GREEN_CONTINUE

Health: GREEN_CONTINUE

Classification: POST_R10_RUNTIME_CLEAN_READY_FOR_30G

Blockers: []

Review: []

Selected dataset candidate:

```json
{
  "dataset_id_guess": "replay",
  "decision_like": [
    "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/strategy_decisions.json",
    "run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_20260418_073935_16057e37/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/artifacts/strategy_decisions.json",
    "run/replay/replay_locked_single_day_phase_a4_true_owner_rerun_20260418_173649_9e3c2c88/artifacts/strategy_decisions.json"
  ],
  "file_count": 2199,
  "frame_like": [
    "run/replay/_phase_a4_row_context_overlay_real_check/baseline_frames.json",
    "run/replay/_phase_a4_row_context_overlay_real_check/shadow_frames.json",
    "run/replay/frame_export_smoke/baseline_frames.json",
    "run/replay/frame_export_smoke/shadow_frames.json",
    "run/replay/frame_export_smoke/comparison_output/profile_snapshot.json",
    "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/features_rows.json",
    "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/features_rows.json",
    "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/features_rows.json",
    "run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/features_rows.json",
    "run/replay/phasea3_true_comparison_20260418_185245/profile_snapshot.json",
    "run/replay/phasea3_true_cmp_frames_20260418_185245/baseline_frames.json",
    "run/replay/phasea3_true_cmp_frames_20260418_185245/shadow_frames.json",
    "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/artifacts/features_rows.json",
    "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/artifacts/features_rows.json",
    "run/replay/true_cmp_frames_20260418_182835/baseline_frames.json"
  ],
  "json_count": 2008,
  "manifest_like": [
    "run/replay/raw_o_label_enriched_20260501_142509/label_enrichment_manifest.json",
    "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/00_manifest.json",
    "run/replay/raw_q_trade_family_backfill_20260501_143325/trade_family_backfill_manifest.json",
    "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/00_manifest.json",
    "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/00_manifest.json",
    "run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/00_manifest.json",
    "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/00_manifest.json",
    "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/00_manifest.json",
    "run/replay/replay_experiment_parameter_sweep_87afd861a2ee43c9/experiments/00_experiment_manifest.json",
    "run/replay/raw_t_post_raw_s_replay_rerun_20260501_151908_raw_s_export/enrichment_manifest.json"
  ],
  "parquet_count": 3,
  "path": "run/replay",
  "provider_like": [
    "run/replay/2026-04-17/fut_ticks.jsonl",
    "run/replay/2026-04-17/opt_ticks.jsonl",
    "run/replay/raw_aa10n_feed_input_adapter_export_20260501_193317/feed_input_declaration.json",
    "run/replay/raw_aa10n_feed_input_adapter_export_20260501_193317/2026-04-17/feed_input_declaration.json",
    "run/replay/raw_aa10n_feed_input_adapter_export_20260501_193317/2026-04-17/ticks_opt/instrument_type=PE/underlying_symbol=NIFTY/expiry=2026-04-23/option_type=PE/strike=22000/ticks_opt.parquet",
    "run/replay/raw_aa10n_feed_input_adapter_export_20260501_193317/2026-04-17/ticks_opt/instrument_type=CE/underlying_symbol=NIFTY/expiry=2026-04-23/option_type=CE/strike=22000/ticks_opt.parquet",
    "run/replay/raw_aa10n_feed_input_adapter_export_20260501_193317/2026-04-17/ticks_fut/instrument_type=FUT/underlying_symbol=NIFTY/expiry=2026-04-23/option_type=__null__/strike=__null__/ticks_fut.parquet",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/04_future_execution_contract.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_only_guarded_provider_feature_summary_patch_29aw/00_replay_only_guarded_provider_feature_summary_patch_report.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_only_guarded_provider_feature_summary_patch_29aw/02_next_provider_feature_summary_validation_contract.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/runtime_feature_field_inventory_contract_29cm/05_future_inventory_template.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/provider_feature_summary_validation_29ax/00_provider_feature_summary_validation_report.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/provider_feature_summary_validation_29ax/02_guarded_replay_provider_feature_summary.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/provider_feature_summary_validation_29ax/01_provider_feature_value_comparison_readiness_decision.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/provider_feature_value_not_comparable_audit_29as/02_provider_feature_parity_blocker_report.json"
  ],
  "reasons": [
    "manifest_json",
    "summary_or_proof_json",
    "parquet",
    "frame_feature_snapshot",
    "decision_artifact",
    "provider_feed_artifact",
    "replay_parity_artifact",
    "multi_file_dir",
    "nonempty_bytes"
  ],
  "replay_like": [
    "run/replay/batch24_broad_replay_materialized_events.jsonl",
    "run/replay/batch23_strong_replay_sample_events.jsonl",
    "run/replay/batch22_aftermarket_semantic_replay_events.jsonl",
    "run/replay/raw_o_label_enriched_20260501_142509/label_enriched_replay_records.jsonl",
    "run/replay/frame_export_smoke/comparison_output/06_blocker_diff_report.json",
    "run/replay/frame_export_smoke/comparison_output/07_economics_diff_report.json",
    "run/replay/frame_export_smoke/comparison_output/05_candidate_diff_report.json",
    "run/replay/frame_export_smoke/comparison_output/11_differential_report.json",
    "run/replay/phasea3_true_comparison_20260418_185245/21_comparison_summary.csv",
    "run/replay/phasea3_true_comparison_20260418_185245/06_blocker_diff_report.json",
    "run/replay/phasea3_true_comparison_20260418_185245/20_comparison_summary.json",
    "run/replay/phasea3_true_comparison_20260418_185245/07_economics_diff_report.json",
    "run/replay/phasea3_true_comparison_20260418_185245/05_candidate_diff_report.json",
    "run/replay/phasea3_true_comparison_20260418_185245/11_differential_report.json",
    "run/replay/replay_experiment_parameter_sweep_87afd861a2ee43c9/experiments/03_differential_summary.json"
  ],
  "score": 110,
  "summary_like": [
    "run/replay/_phase_a4_closure_proof.json",
    "run/replay/raw_o_label_enriched_20260501_142509/label_enrichment_summary.json",
    "run/replay/frame_export_smoke/comparison_output/06_blocker_diff_report.json",
    "run/replay/frame_export_smoke/comparison_output/09_put_leg_focus_report.json",
    "run/replay/frame_export_smoke/comparison_output/04_metrics_summary.json",
    "run/replay/frame_export_smoke/comparison_output/08_side_split_report.json",
    "run/replay/frame_export_smoke/comparison_output/07_economics_diff_report.json",
    "run/replay/frame_export_smoke/comparison_output/05_candidate_diff_report.json",
    "run/replay/frame_export_smoke/comparison_output/11_differential_report.json",
    "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/04_metrics_summary.json"
  ],
  "total_bytes": 1573851446
}
```

Next: Batch 30G — selected dataset structure validator, offline only; no replay execution yet.

Safety: no patch, no service stop/start, no Redis delete, no paper/live, no orders, no replay execution.
