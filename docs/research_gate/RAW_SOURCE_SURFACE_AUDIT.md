# RAW-A — Source Surface Audit

Date: 2026-05-01
Generated UTC: 2026-05-01T07:09:52.894711+00:00
Batch tag: batch_raw_a_b_freeze_final_v2_20260501_123952
Source mode: sanitized_archive
Archive: /home/Lenovo/scalpx/projects/mme_scalpx/run/evidence_bundles/batch27a_replay_full_audit_bundle_20260501_095926_SANITIZED.tar.gz
Resolved source root: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle

## Purpose

This audit freezes the source-surface map before RAW / Research Gate implementation.

RAW must be a non-live, non-mutating evidence layer above research_capture and replay.

RAW must not duplicate raw capture, write live Redis truth, send orders, mutate strategy doctrine, enable paper/live, or bypass risk/execution.

## Target artifact backup status before write

| Path | Existed | Lines | SHA256 | Backup |
|---|---:|---:|---|---|
| `docs/research_gate/RAW_SOURCE_SURFACE_AUDIT.md` | False | None | `None` | `None` |
| `docs/research_gate/RAW_RESEARCH_GATE_CONSTITUTION.md` | False | None | `None` | `None` |
| `run/proofs/proof_raw_source_surface_audit.json` | False | None | `None` | `None` |
| `run/proofs/proof_raw_constitution_freeze.json` | False | None | `None` | `None` |
| `run/proofs/proof_raw_a_b_freeze_final.json` | False | None | `None` | `None` |

## Live evidence audit track

Live evidence answers: what did the real running system capture, emit, decide, and protect?

It should inspect feed health, Dhan/OI context availability, family surfaces, decision streams, order safety, provider runtime, and no-live-order proofs.

| Surface | Exists | Kind | Files | Owner | RAW interpretation |
|---|---:|---|---:|---|---|
| `app/mme_scalpx/services/feeds.py` | True | file | 1 | live_runtime | Live feed owner. RAW must not ingest directly or duplicate feed ownership. |
| `app/mme_scalpx/services/features.py` | True | file | 1 | live_runtime | Feature producer. RAW may consume archived feature artifacts, not mutate live features. |
| `app/mme_scalpx/services/strategy.py` | True | file | 1 | live_runtime | Strategy decision owner. RAW must not become live strategy engine. |
| `app/mme_scalpx/services/risk.py` | True | file | 1 | live_runtime | Risk veto owner. RAW must not override risk. |
| `app/mme_scalpx/services/execution.py` | True | file | 1 | live_runtime | Execution/broker/position owner. RAW must not place orders. |
| `app/mme_scalpx/core/names.py` | True | file | 1 | spine | Canonical names surface. |
| `app/mme_scalpx/core/models.py` | True | file | 1 | spine | Canonical schema/model surface. |
| `run/live_capture` | False | missing | 0 | artifact | Live capture logs/artifacts if present. RAW may read as evidence. |
| `run/proofs` | True | dir | 786 | artifact | Proof artifacts. RAW may read as evidence. |

## Replay evidence audit track

Replay evidence answers: what would the strategies have done across historical or replayed market conditions?

It should inspect replay outputs, baseline vs shadow results, PnL, missed trades, false entries, blocker quality, OI-wall impact, strategy ranking, and market-regime behavior.

| Surface | Exists | Kind | Files | Owner | RAW interpretation |
|---|---:|---|---:|---|---|
| `app/mme_scalpx/replay` | True | dir | 20 | replay | Replay/backtest owner. RAW consumes replay outputs; it does not replace replay. |
| `run/replay` | True | dir | 650 | artifact | Replay run artifacts if present. |
| `app/mme_scalpx/research_capture` | True | dir | 25 | research_capture | Raw/historical capture owner. Preserve and reuse; do not duplicate. |
| `etc/research_capture` | True | dir | 12 | research_capture_config | Capture policy/config owner. |
| `etc/strategy_family` | True | dir | 21 | strategy_family_config | Frozen family doctrine/config surfaces. |

## Future RAW surfaces

These are future owners and must not be created in RAW-A/B except documentation/proof references.

| Surface | Exists | Kind | Files | Owner | RAW interpretation |
|---|---:|---|---:|---|---|
| `app/mme_scalpx/research_gate` | False | missing | 0 | future_raw | Future RAW package. RAW-A/B should not create code here yet. |
| `etc/research_gate` | False | missing | 0 | future_raw_config | Future RAW config. RAW-A/B should not create config here yet. |
| `run/research_gate` | False | missing | 0 | future_raw_artifacts | Future RAW report output path. |

## Path discovery

### research_capture

- `etc/research_capture/integrity_policy.json`
- `etc/research_capture/partitions.json`
- `etc/research_capture/research_policy.json`
- `etc/research_capture/operator_defaults.json`
- `etc/research_capture/report_policy.json`
- `etc/research_capture/config_registry.json`
- `etc/research_capture/schema_version.json`
- `etc/research_capture/backfill_policy.json`
- `etc/research_capture/source_policy.json`
- `etc/research_capture/runtime_policy.json`
- `etc/research_capture/export_policy.json`
- `etc/research_capture/archive_config.json`
- `run/proofs/research_capture_contracts.json`
- `run/proofs/proof_research_capture_production_firewall.json`
- `run/research_capture/2026-04-17/source_availability.json`
- `run/research_capture/2026-04-17/manifest.json`
- `run/research_capture/2026-04-17/integrity_summary.json`
- `run/research_capture/2026-04-18/source_availability.json`
- `run/research_capture/2026-04-18/manifest.json`
- `run/research_capture/2026-04-18/integrity_summary.json`
- `run/research_capture/2026-04-01/source_availability.json`
- `run/research_capture/2026-04-01/manifest.json`
- `run/research_capture/2026-04-01/integrity_summary.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/source_availability.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/manifest.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/effective_inputs.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/session_materialization_report.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/integrity_report.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/artifact_materialization_report.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/integrity_summary.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/manifest_materialization_report.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/health_snapshot.json`
- `run/research_capture/reports/research_capture_manifest_report_surface_proof_20260419_092158/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/source_availability.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/manifest.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/integrity_report.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/integrity_summary.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/manifest_materialization_report.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/health_snapshot.json`
- `run/research_capture/reports/rcap_backfill_routeaudit_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_verify_mat_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_verify_mat_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_verify_mat_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_verify_mat_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/source_availability.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/manifest.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/integrity_summary.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/manifest_materialization_report.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/run_report.json`
- `run/research_capture/reports/rcap_run_bridge_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/source_availability.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/manifest.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/effective_inputs.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/session_materialization_report.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/research_report.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/integrity_summary.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/manifest_materialization_report.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/research_inventory.json`
- `run/research_capture/reports/rcap_research_operational_20260418_greencheck/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_run_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_run_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/source_availability.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/manifest.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/integrity_summary.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/manifest_materialization_report.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/health_snapshot.json`
- `run/research_capture/reports/rcap_run_operational_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_verify_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_verify_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_backfill_mat_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_backfill_mat_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_backfill_mat_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_backfill_mat_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_research_range_mat_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_research_range_mat_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_research_range_mat_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_research_range_mat_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/source_availability.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/manifest.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/effective_inputs.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/session_materialization_report.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/integrity_report.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/artifact_materialization_report.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/integrity_summary.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/manifest_materialization_report.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/health_snapshot.json`
- `run/research_capture/reports/research_capture_backfill_20260418_231342/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_run_session_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_run_session_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_research_session_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_research_session_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/source_availability.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/manifest.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/integrity_report.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/integrity_summary.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/manifest_materialization_report.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/health_snapshot.json`
- `run/research_capture/reports/rcap_run_operational_routeaudit_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/source_availability.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/manifest.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/effective_inputs.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/session_materialization_report.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/artifact_materialization_report.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/integrity_summary.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/manifest_materialization_report.json`
- `run/research_capture/reports/rcap_run_raw_real_fix1_20260418_demo/effective_registry_snapshot.json`
- `run/research_capture/reports/rcap_verify_manifest_20260418_demo/source_availability.json`

### replay

- `REPLAY_CONTRACT_GREP_INDEX.txt`
- `README_REPLAY_FULL_AUDIT_PURPOSE.txt`
- `SUGGESTED_REPLAY_PROOF_COMMANDS.txt`
- `REPLAY_FULL_AUDIT_RUBRIC.md`
- `REPLAY_FILE_INVENTORY.txt`
- `GIT_DIFF_REPLAY_RELEVANT.txt`
- `etc/replay/schemas/replay_run_manifest.schema.json`
- `etc/replay/datasets/replay_feed_input_contract_v1.sample.json`
- `etc/replay/datasets/replay_dataset_capability_profile_economics_enriched_v1.json`
- `etc/replay/datasets/replay_dataset_capability_quote_only_v1.json`
- `etc/replay/datasets/replay_dataset_capability_economics_enriched_v1.json`
- `etc/replay/datasets/replay_dataset_declaration_replay_dataset_2026_04_17_enriched_v1.json`
- `etc/replay/datasets/replay_feed_input_contract_v1.json`
- `etc/replay/datasets/replay_dataset_capability_profile_quote_only_v1.json`
- `etc/replay/datasets/replay_dataset_declaration_replay_dataset_2026_04_17_v1.json`
- `etc/replay/experiments/shadow_vel12_putrc15.yaml`
- `etc/replay/profiles/cmp_locked_vs_shadow_vel12_putrc15.yaml`
- `run/proofs/proof_risk_replay_key_separation.json`
- `run/proofs/recorded_live_replay_readiness_latest.json`
- `run/proofs/proof_aftermarket_historical_replay_readiness.json`
- `run/proofs/shadow_replay_econ_off_confirm1_t35_s10_summary_2026-04-16.json`
- `run/proofs/shadow_replay_econ_off_confirm1_summary_2026-04-16.json`
- `run/proofs/shadow_replay_econ_off_confirm1_signal_entry_summary_2026-04-16.json`
- `run/proofs/proof_aftermarket_full_replay_dry_run.json`
- `run/proofs/replay_zero_injection_diagnosis_latest.json`
- `run/proofs/shadow_replay_econ_off_confirm1_summary_2026-04-17.json`
- `run/proofs/proof_aftermarket_broad_replay_materialization.json`
- `run/proofs/shadow_replay_econ_off_summary_2026-04-17.json`
- `run/proofs/replay_batch16_freeze.json`
- `run/proofs/shadow_replay_econ_off_confirm1_trade_analysis_2026-04-16.txt`
- `run/proofs/proof_aftermarket_strong_replay_sample.json`
- `run/proofs/day_filtered_replay_dataset_latest.json`
- `run/proofs/proof_oi_replay_report_impact.json`
- `run/proofs/batch23_recovery_clean_hygiene_replay_gate_20260425_195357_remaining_pycache.txt`
- `run/proofs/shadow_replay_econ_off_summary_2026-04-16.json`
- `run/proofs/shadow_replay_econ_off_confirm1_signal_entry_summary_2026-04-17.json`
- `run/proofs/replay_stage_output_gap_inspection_20260425_150911.json`
- `run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/full_pipeline_stage_summary.json`
- `run/proofs/replay_comparison_spec_2026-04-17/03_operator_handoff.txt`
- `run/proofs/replay_comparison_spec_2026-04-17/00_study_brief.txt`
- `run/proofs/replay_comparison_spec_2026-04-17/01_replay_comparison_spec.json`
- `run/proofs/replay_comparison_spec_2026-04-17/02_replay_comparison_spec.txt`
- `run/proofs/recorded_live_replay_readiness_20260425_135322/recorded_live_replay_readiness_latest.json`
- `run/proofs/post_replay_validation_checkpoint_20260425_195340/git_diff_name_only.txt`
- `run/proofs/post_replay_validation_checkpoint_20260425_195340/checkpoint.json`
- `run/proofs/post_replay_validation_checkpoint_20260425_195340/git_status_short.txt`
- `run/proofs/day_filtered_replay_dataset_20260425_155247/day_filtered_manifest.json`
- `run/proofs/replay_compatibility_audit_20260425_150508/input_files.txt`
- `run/proofs/replay_compatibility_audit_20260425_150508/replay_compatibility_plan.json`
- `run/proofs/replay_compatibility_audit_20260425_150508/replay_compatibility_summary.json`
- `run/proofs/replay_compatibility_audit_20260425_150508/run_artifact_inventory.txt`
- `run/proofs/replay_zero_injection_diagnosis_20260425_151003/replay_zero_injection_diagnosis_latest.json`
- `run/proofs/replay_quote_compat_20260425_150651/replay_quote_compat_summary.json`
- `run/proofs/replay_quote_compat_20260425_150651/run_artifact_inventory.txt`
- `run/proofs/replay_integrity_fail_diagnosis_20260425_152144/replay_integrity_fail_diagnosis.json`
- `run/replay/_phase_a4_closure_proof.json`
- `run/replay/_phase_a4_true_owner_rerun_inputs.json`
- `run/replay/_phase_a4_row_context_overlay_real_check/baseline_frames.json`
- `run/replay/_phase_a4_row_context_overlay_real_check/shadow_frames.json`
- `run/replay/frame_export_smoke/baseline_frames.json`
- `run/replay/frame_export_smoke/shadow_frames.json`
- `run/replay/frame_export_smoke/comparison_output/12_operator_verdict.txt`
- `run/replay/frame_export_smoke/comparison_output/06_blocker_diff_report.json`
- `run/replay/frame_export_smoke/comparison_output/09_put_leg_focus_report.json`
- `run/replay/frame_export_smoke/comparison_output/04_metrics_summary.json`
- `run/replay/frame_export_smoke/comparison_output/shadow_override_flattened.json`
- `run/replay/frame_export_smoke/comparison_output/08_side_split_report.json`
- `run/replay/frame_export_smoke/comparison_output/07_economics_diff_report.json`
- `run/replay/frame_export_smoke/comparison_output/05_candidate_diff_report.json`
- `run/replay/frame_export_smoke/comparison_output/11_differential_report.json`
- `run/replay/frame_export_smoke/comparison_output/profile_snapshot.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/00_manifest.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/02_scope_profile.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/04_metrics_summary.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/03_integrity_report.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/01_dataset_summary.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/17_effective_inputs.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/18_effective_overrides_flat.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/10_run_summary.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/strategy_decisions.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/risk_outputs.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/engine_result.json`
- `run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/features_rows.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/00_manifest.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/02_scope_profile.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/04_metrics_summary.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/03_integrity_report.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/01_dataset_summary.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/17_effective_inputs.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/18_effective_overrides_flat.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/10_run_summary.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/strategy_decisions.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/risk_outputs.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/engine_result.json`
- `run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/features_rows.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/00_manifest.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/02_scope_profile.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/04_metrics_summary.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/03_integrity_report.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/01_dataset_summary.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/17_effective_inputs.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/18_effective_overrides_flat.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/strategy_decisions.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/risk_outputs.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/engine_result.json`
- `run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/features_rows.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/00_manifest.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/02_scope_profile.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/04_metrics_summary.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/03_integrity_report.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/01_dataset_summary.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/17_effective_inputs.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/18_effective_overrides_flat.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/10_run_summary.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/strategy_decisions.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/risk_outputs.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/engine_result.json`
- `run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/features_rows.json`
- `run/replay/phasea3_true_comparison_20260418_185245/12_operator_verdict.txt`
- `run/replay/phasea3_true_comparison_20260418_185245/06_blocker_diff_report.json`

### dhan_context

- `etc/brokers/dhan.yaml`
- `run/proofs/proof_dhan_context_quality.json`
- `run/proofs/proof_batch25v_dhan_context_completeness_audit.json`
- `run/proofs/proof_dhan_execution_fallback_policy.json`
- `run/proofs/proof_dhan_context_adapter_ladder_payload.json`
- `run/proofs/proof_dhan_oi_ladder_persistence.json`
- `run/proofs/proof_batch25v_orphan_lock_cleanup_after_dhan_429.json`
- `run/proofs/batch26o4_feed_snapshot_publication_20260430_225806_inspection/app_mme_scalpx_integrations_dhan_marketdata_py_grep.txt`
- `app/mme_scalpx/integrations/dhan_execution.py`
- `app/mme_scalpx/integrations/dhan_marketdata.py`
- `app/mme_scalpx/integrations/dhan_runtime_clients.py`
- `docs/milestones/2026-04-26_batch25j_dhan_oi_ladder_context_freeze.md`
- `bin/proof_dhan_context_quality.py`
- `bin/dhan_nifty_capability_audit.py`
- `bin/proof_dhan_oi_ladder_persistence.py`
- `bin/audit_dhan_context_completeness_25v.py`
- `bin/proof_dhan_execution_fallback_policy.py`
- `bin/dhan_mcx_option_probe.py`
- `bin/proof_dhan_context_adapter_ladder_payload.py`
- `bin/dhan_closed_market_feeds_features_check.py`

### oi_wall_or_oi_context

- `run/proofs/proof_oi_context_surface_audit.json`
- `run/proofs/proof_oi_wall_authority_canonicalized.json`
- `run/proofs/proof_oi_wall_authority_canonicalized_r2_failure_diagnostic_20260430_000536.json`
- `run/proofs/proof_dhan_oi_ladder_persistence.json`
- `run/proofs/proof_oi_context_surface_audit_r1_failure_diagnostic_20260429_235424.json`
- `run/proofs/proof_oi_replay_report_impact.json`
- `run/proofs/proof_oi_family_soft_scoring.json`
- `docs/milestones/2026-04-30_batch26_oi_b_wall_authority_canonicalized.md`
- `docs/milestones/2026-04-30_batch26_oi_d_replay_report_impact.md`
- `docs/milestones/2026-04-29_batch26_oi_a_surface_audit.md`
- `docs/milestones/2026-04-30_batch26_oi_c_family_soft_scoring.md`
- `docs/milestones/2026-04-26_batch25j_dhan_oi_ladder_context_freeze.md`
- `bin/proof_oi_context_surface_audit.py`
- `bin/proof_oi_family_soft_scoring.py`
- `bin/proof_dhan_oi_ladder_persistence.py`
- `bin/proof_oi_replay_report_impact.py`
- `bin/proof_oi_wall_authority_canonicalized.py`

### family_surfaces

- `run/proofs/family_features_offline_put_breakout_misb_misc.json`
- `run/proofs/proof_market_session_family_surfaces.json`
- `run/proofs/feature_family_surfaces_batch9_freeze.json`
- `run/proofs/family_features_offline_misr_fakeout_reversal.json`
- `run/proofs/family_features_offline_call_trend_mist.json`
- `run/proofs/proof_family_features_canonical_support.json`
- `run/proofs/family_surface_sample_after_patch.json`
- `run/proofs/family_features_offline_put_trend_mist.json`
- `run/proofs/proof_family_surface_service_path.json`
- `run/proofs/family_features_offline_miso_option_burst.json`
- `run/proofs/family_features_offline_call_breakout_misb_misc.json`
- `run/proofs/family_features_offline_miso_base_5depth_degraded.json`
- `run/proofs/batch26o1_recovery_singleton_baseline_20260430_224350_inspection/bin__proof_market_session_family_surfaces_py_grep_index.txt`
- `run/proofs/batch26o5_live_key_topology_20260430_230005_inspection/bin_proof_market_session_family_surfaces_py_grep.txt`
- `run/proofs/batch26o8_live_25v_gate_20260430_232336_inspection/bin_proof_market_session_family_surfaces_py_grep.txt`
- `docs/milestones/2026-04-26_batch25m_canonical_family_features_repair.md`
- `docs/milestones/2026-04-26_batch25l_family_surface_service_path_repair.md`
- `docs/milestones/2026-04-25_batch9_feature_family_surfaces_corrective_freeze_final.md`
- `docs/strategy/MIS_FAMILY_SURFACE_REGISTRY.md`
- `bin/proof_market_session_family_surfaces.py`
- `bin/proof_feature_family_surfaces_batch9_freeze.py`
- `bin/proof_family_features_offline.py`
- `bin/proof_family_surface_service_path.py`
- `bin/proof_family_features_canonical_support.py`

### proof_scripts_or_outputs

- `SUGGESTED_REPLAY_PROOF_COMMANDS.txt`
- `PROOF_ARTIFACT_INVENTORY.txt`
- `PROOF_SCRIPT_INVENTORY.txt`
- `etc/proof_registry.yaml`
- `run/proofs/proof_layer_contracts_20260425_133516.json`
- `run/proofs/proof_contract_field_registry.json`
- `run/proofs/proof_risk_replay_key_separation.json`
- `run/proofs/proof_provider_runtime_contract_seam.json`
- `run/proofs/proof_batch25v_single_start_lock_forensics.json`
- `run/proofs/proof_feature_raw_selected_split.json`
- `run/proofs/proof_5family_producer_consumer_matrix.json`
- `run/proofs/proof_paper_armed_readiness_gate.json`
- `run/proofs/proof_batch26o4_feed_snapshot_publication.json`
- `run/proofs/proof_batch25v_feeds_lock_cleanup_after_orphan_stop.json`
- `run/proofs/proof_runtime_truth_authority.json`
- `run/proofs/proof_batch26o3_provider_runtime_publication.json`
- `run/proofs/proof_5family_integration_master.json`
- `run/proofs/proof_config_runtime_truth.json`
- `run/proofs/proof_5family_closed_market_dryrun.json`
- `run/proofs/proof_aftermarket_historical_replay_readiness.json`
- `run/proofs/proof_market_session_feed_snapshot.json`
- `run/proofs/proof_selected_option_active_bridge.json`
- `run/proofs/proof_batch25s_ancillary_completeness.json`
- `run/proofs/proof_paper_armed_readiness_gate_market_closed_stop.json`
- `run/proofs/proof_batch26n_scope_shadow_vs_paper_20260430_111929.json`
- `run/proofs/proof_feature_selected_side_isolation.json`
- `run/proofs/proof_batch26o8_live_25v_gate.json`
- `run/proofs/proof_oi_context_surface_audit.json`
- `run/proofs/proof_paper_armed_readiness_gate_v2.json`
- `run/proofs/proof_batch25v_feeds_lock_owner_before_cleanup.json`
- `run/proofs/proof_features_false_readiness_guards.json`
- `run/proofs/proof_systemd_runtime_alignment.json`
- `run/proofs/proof_miso_provider_doctrine_alignment.json`
- `run/proofs/proof_paper_armed_readiness_gate_v3.json`
- `run/proofs/proof_market_session_family_surfaces.json`
- `run/proofs/proof_batch26k_controlled_paper_prestart_readiness.json`
- `run/proofs/proof_batch26m_readonly_capture_safety_20260430_101743.json`
- `run/proofs/proof_batch25v_runtime_lock_cleanup_restart_disabled.json`
- `run/proofs/proof_batch26o7_controlled_runtime_start_preflight.json`
- `run/proofs/proof_alias_and_override_inventory.json`
- `run/proofs/proof_runtime_dependency_lock.json`
- `run/proofs/proof_execution_hold_no_order.json`
- `run/proofs/proof_strategy_family_reverse_coverage.json`
- `run/proofs/proof_runtime_config_alignment.json`
- `run/proofs/proof_features_active_vs_context_option_truth.json`
- `run/proofs/proof_layer_contracts_20260425_132522.json`
- `run/proofs/proof_batch26o_last20_live_market_pack_20260430_150530.json`
- `run/proofs/proof_batch26o2_position_flat_reseed_guard.json`
- `run/proofs/proof_dhan_context_quality.json`
- `run/proofs/proof_batch26o0_disk_redis_recovery_20260430_150149.json`
- `run/proofs/proof_logging_redaction.json`
- `run/proofs/proof_feature_side_direct_member_surface.json`
- `run/proofs/proof_risk_gate_execution_integration.json`
- `run/proofs/proof_aftermarket_full_replay_dry_run.json`
- `run/proofs/proof_risk_controlled_paper_veto.json`
- `run/proofs/batch26i_proof_layer_upgrade.json`
- `run/proofs/proof_layer_contracts.json`
- `run/proofs/proof_layer_contracts_20260425_130942.json`
- `run/proofs/proof_execution_entry_contract_dryrun.json`
- `run/proofs/proof_batch26o6_observer_guard.json`
- `run/proofs/proof_oi_wall_authority_canonicalized.json`
- `run/proofs/proof_provider_auth_sources.json`
- `run/proofs/proof_oi_wall_authority_canonicalized_r2_failure_diagnostic_20260430_000536.json`
- `run/proofs/proof_batch25v_dhan_context_completeness_audit.json`
- `run/proofs/proof_feeds_provider_surface_strictness.json`
- `run/proofs/proof_market_session_strategy_activation.json`
- `run/proofs/proof_family_features_canonical_support.json`
- `run/proofs/proof_misr_trap_event_consumption_registry.json`
- `run/proofs/proof_alias_and_override_inventory_focused_triage.json`
- `run/proofs/proof_controlled_paper_runtime_wiring.json`
- `run/proofs/proof_market_session_no_order_sent.json`
- `run/proofs/proof_dhan_execution_fallback_policy.json`
- `run/proofs/proof_aftermarket_broad_replay_materialization.json`
- `run/proofs/proof_layer_contracts_20260425_133432.json`
- `run/proofs/proof_layer_contracts_20260425_210412.json`
- `run/proofs/proof_miso_burst_event_consumption_registry.json`
- `run/proofs/proof_risk_controlled_paper_veto_patch_step.json`
- `run/proofs/proof_layer_contracts_20260425_133318.json`
- `run/proofs/proof_dhan_context_adapter_ladder_payload.json`
- `run/proofs/proof_batch26o1_recovery_singleton_baseline.json`
- `run/proofs/proof_batch26o_live_key_surface_map_20260430_152940.json`
- `run/proofs/proof_runtime_instrument_provider_equivalence.json`
- `run/proofs/proof_layer_contracts_20260425_132531.json`
- `run/proofs/proof_dhan_oi_ladder_persistence.json`
- `run/proofs/proof_layer_contracts_20260425_132852.json`
- `run/proofs/proof_layer_contracts_20260425_125305.json`
- `run/proofs/proof_risk_trade_ledger_idempotency.json`
- `run/proofs/proof_family_surface_service_path.json`
- `run/proofs/proof_report_service_forbidden_path_fix_20260430_094328.txt`
- `run/proofs/proof_oi_context_surface_audit_r1_failure_diagnostic_20260429_235424.json`
- `run/proofs/proof_aftermarket_strong_replay_sample.json`
- `run/proofs/proof_legacy_quarantine_import_graph.json`
- `run/proofs/proof_order_intent_adapter_disabled.json`
- `run/proofs/proof_monitor_redis_attr_contract.json`
- `run/proofs/proof_batch26n_final_live_observation_summary_20260430_121718.json`
- `run/proofs/proof_lock_refresh_contract.json`
- `run/proofs/proof_market_session_feature_payload.json`
- `run/proofs/proof_oi_replay_report_impact.json`
- `run/proofs/proof_research_capture_production_firewall.json`
- `run/proofs/proof_batch25v_orphan_lock_cleanup_after_dhan_429.json`
- `run/proofs/proof_feed_snapshot_feature_adapter.json`
- `run/proofs/proof_live_safe_observe_after_paper_abort_20260430_120656.json`
- `run/proofs/proof_risk_restart_rebuild.json`
- `run/proofs/proof_legacy_quarantine_import_graph_repair.json`
- `run/proofs/proof_no_live_order_hard_guard.json`
- `run/proofs/proof_no_live_order_hard_guard_r1.json`
- `run/proofs/proof_feature_call_put_side_separation.json`
- `run/proofs/proof_batch26m_readonly_capture_safety_final_20260430_101901.json`
- `run/proofs/proof_feeds_lock_refresh_pre_poll.json`
- `run/proofs/proof_oi_family_soft_scoring.json`
- `run/proofs/proof_batch26d_strategy_leaf_required_surface_failclosed.json`
- `run/proofs/proof_alias_and_override_inventory_focused_triage_v2.json`
- `run/proofs/proof_main_bootstrap_provider_report_contract.json`
- `run/proofs/proof_layer_contracts_20260425_210017.json`
- `run/proofs/proof_batch25v_feeds_lock_cleanup.json`
- `run/proofs/proof_batch25v_final_summary.json`
- `run/proofs/proof_layer_contracts_20260425_210233.json`
- `run/proofs/proof_misr_trap_event_consumption_registry_patch_step.json`
- `run/proofs/proof_feature_family_shared_builder_abi.json`
- `run/proofs/proof_layer_contracts_20260425_133015.json`

## RAW-A conclusion

RAW should analyze live and replay separately, then compare them.

Live audit protects runtime safety and data trust.

Replay audit gives richer strategy, PnL, blocker, missed-trade, false-entry, OI-wall, and market-regime evidence.

Correct RAW equation:

live evidence + replay evidence + parity comparison = promotion-grade research evidence

## RAW-A verdict

PASS.

This batch only writes docs/proofs/milestone artifacts and does not modify runtime code.
