# MME-ScalpX Bin Migration Plan

Generated: 2026-05-11T23:14:41.713244

## Status

This is a plan-only document. No files were moved.

## Safety

- No files moved.
- No files deleted.
- No services started.
- No broker calls.
- No Redis writes.
- No paper/live enablement.

## R4 Summary

- total_bin_files: 407
- unknown_count: 7
- high_review_count: 343

## R5 Unknown Resolution

### `bin/check_broker_token.py`

- resolved_kind: `manual_review_required`
- recommended_bucket: `bin/unclassified_review_required/`
- reason: no safe automatic classification

### `bin/dhan_mcx_option_probe.py`

- resolved_kind: `manual_review_required`
- recommended_bucket: `bin/unclassified_review_required/`
- reason: no safe automatic classification

### `bin/ensure_zerodha_shared_token.py`

- resolved_kind: `manual_review_required`
- recommended_bucket: `bin/unclassified_review_required/`
- reason: no safe automatic classification

### `bin/export_session_artifacts.py`

- resolved_kind: `diagnostic`
- recommended_bucket: `bin/diagnostics/`
- reason: content references Redis/inspection style operations

### `bin/feed_depth_witness.py`

- resolved_kind: `manual_review_required`
- recommended_bucket: `bin/unclassified_review_required/`
- reason: no safe automatic classification

### `bin/predischeck.py`

- resolved_kind: `diagnostic`
- recommended_bucket: `bin/diagnostics/`
- reason: content references Redis/inspection style operations

### `bin/top20.sh`

- resolved_kind: `manual_review_required`
- recommended_bucket: `bin/unclassified_review_required/`
- reason: no safe automatic classification

## Risk Flag Counts

- BROKER_MENTION: 151
- ORDER_MENTION: 141
- REDIS_MENTION: 167
- RUNTIME_START_MENTION: 93
- SYSTEMD_MENTION: 4

## Future Target Buckets

### bin/controlled_paper/

- planned_count: 4

  - `bin/__pycache__/run_batch26o11_controlled_paper_monitor.cpython-310.pyc`
  - `bin/__pycache__/start_batch26o10_controlled_paper.cpython-310.pyc`
  - `bin/__pycache__/start_controlled_paper_runtime_chain.cpython-310.pyc`
  - `bin/batch26m_enable_controlled_paper_from_25v25w.sh`

### bin/diagnostics/

- planned_count: 9

  - `bin/audit_dhan_context_completeness_25v.py`
  - `bin/audit_recorded_live_data_clean_inventory.py`
  - `bin/audit_session_exports_schema.py`
  - `bin/batch26o8a_after_market_closure_audit.py`
  - `bin/dhan_nifty_capability_audit.py`
  - `bin/export_session_artifacts.py`
  - `bin/live_session_forensics_readonly.py`
  - `bin/post_market_session_forensics.py`
  - `bin/predischeck.py`

### bin/observe_only/

- planned_count: 5

  - `bin/live_signal_forensics_observer.py`
  - `bin/mme_live_observer.py`
  - `bin/observe_only_live_evidence_collect.py`
  - `bin/observe_only_market_session_capture_execute.py`
  - `bin/observe_strategy_activation_report_live.py`

### bin/patches/

- planned_count: 3

  - `bin/patch_batch26b_execution_hard_arming_guard_thin.py`
  - `bin/patch_batch26c_risk_controlled_paper_veto.py`
  - `bin/patch_batch26d_strategy_leaf_required_surface_failclosed.py`

### bin/proofs/

- planned_count: 152

  - `bin/__pycache__/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.cpython-310.pyc`
  - `bin/__pycache__/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.cpython-310.pyc`
  - `bin/__pycache__/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.cpython-310.pyc`
  - `bin/__pycache__/proof_batch26o23_j_post_repair_controlled_paper_observation.cpython-310.pyc`
  - `bin/_batch25v_market_observation_common.py`
  - `bin/_final_static_proof_helpers.py`
  - `bin/batch26o2_deep_blocker_analysis.py`
  - `bin/build_proof_bundle.py`
  - `bin/export_runtime_truth_evidence.py`
  - `bin/getfile`
  - `bin/prepair_safe.py`
  - `bin/proof_5family_integration_master.py`
  - `bin/proof_actual_replay_engine_integration_preflight_28q.py`
  - `bin/proof_aftermarket_full_replay_dry_run.py`
  - `bin/proof_aftermarket_historical_replay_readiness.py`
  - `bin/proof_aftermarket_strong_replay_sample.py`
  - `bin/proof_batch26a_current_repo_truth.py`
  - `bin/proof_batch26b_execution_hard_arming_guard_thin.py`
  - `bin/proof_batch26d_strategy_leaf_required_surface_failclosed.py`
  - `bin/proof_batch26k_controlled_paper_prestart_readiness.py`
  - `bin/proof_batch26o13_activation_bridge_audit.py`
  - `bin/proof_batch26o14_controlled_activation_bridge.py`
  - `bin/proof_batch26o15_activation_candidate_surface_audit.py`
  - `bin/proof_batch26o16_consumer_view_mapping_repair.py`
  - `bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py`
  - `bin/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.py`
  - `bin/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.py`
  - `bin/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.py`
  - `bin/proof_batch26o16d_selected_option_classic_provider_readiness.py`
  - `bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py`
  - `bin/proof_batch26o16f_selected_option_source_to_feature_mapping.py`
  - `bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py`
  - `bin/proof_batch26o16g_selected_option_provider_data_quality_tradability.py`
  - `bin/proof_batch26o16h_final_data_valid_composition.py`
  - `bin/proof_batch26o16h_r2_persistent_final_composition.py`
  - `bin/proof_batch26o17_activation_candidate_extraction.py`
  - `bin/proof_batch26o17a_selected_option_common_abi_sanitizer.py`
  - `bin/proof_batch26o17b_common_parent_abi_sanitizer.py`
  - `bin/proof_batch26o17b_r2_common_abi_proof_correction.py`
  - `bin/proof_batch26o18_lightweight_controlled_paper_preflight.py`
  - `bin/proof_batch26o19_lightweight_controlled_paper_runtime.py`
  - `bin/proof_batch26o1_recovery_singleton_baseline.py`
  - `bin/proof_batch26o20_controlled_paper_extended_observation.py`
  - `bin/proof_batch26o20_r2_bounded_short_observation.py`
  - `bin/proof_batch26o20_r3_corrected_bounded_observation.py`
  - `bin/proof_batch26o20_r3a_persistent_features_abi_publish_repair.py`
  - `bin/proof_batch26o20_r3b_corrected_bounded_observation.py`
  - `bin/proof_batch26o20_r3c_runtime_data_validity_source_audit.py`
  - `bin/proof_batch26o20_r3d_consumer_view_validity_semantics.py`
  - `bin/proof_batch26o20_r3d_r1_consumer_view_semantics_wrapper_repair.py`
  - `bin/proof_batch26o20_r3d_r2_source_publish_repair.py`
  - `bin/proof_batch26o20_r3d_r2a_structural_valid_source_field.py`
  - `bin/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.py`
  - `bin/proof_batch26o20_r3f_persisted_features_publish_route_classifier.py`
  - `bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py`
  - `bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py`
  - `bin/proof_batch26o20r_recovery_after_terminated_o20.py`
  - `bin/proof_batch26o21_controlled_paper_promotion_readiness.py`
  - `bin/proof_batch26o21r_post_o21_orphan_cleanup.py`
  - `bin/proof_batch26o22_controlled_paper_longer_observation_plan.py`
  - `bin/proof_batch26o22_r2_controlled_paper_plan_proof_correction.py`
  - `bin/proof_batch26o22_r3_controlled_paper_static_gate_proof.py`
  - `bin/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.py`
  - `bin/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.py`
  - `bin/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.py`
  - `bin/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.py`
  - `bin/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.py`
  - `bin/proof_batch26o22a_o20r2_o22_proof_chain_consistency.py`
  - `bin/proof_batch26o23_a_r1_session_completion_safety_readback.py`
  - `bin/proof_batch26o23_b_controlled_paper_evidence_review.py`
  - `bin/proof_batch26o23_b_r1_controlled_pid_cleanup_readback.py`
  - `bin/proof_batch26o23_b_r2_evidence_review_correction.py`
  - `bin/proof_batch26o23_c_r1_completion_safety_readback.py`
  - `bin/proof_batch26o23_d_second_session_evidence_review.py`
  - `bin/proof_batch26o23_e_no_candidate_root_cause_review.py`
  - `bin/proof_batch26o23_f_r2_disk_recovery_backup_policy.py`
  - `bin/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.py`
  - `bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py`
  - `bin/proof_batch26o23_g_narrow_bridge_diagnostic.py`
  - `bin/proof_batch26o23_h_narrow_bridge_repair.py`
  - ... 72 more

### bin/replay/

- planned_count: 19

  - `bin/actual_replay_engine_callable_adapter_28t.py`
  - `bin/actual_replay_engine_module_adapter_28r.py`
  - `bin/audit_guarded_replay_engine_runtime_gap_29h.py`
  - `bin/audit_recorded_live_replay_readiness.py`
  - `bin/execute_guarded_offline_replay_dry_run_28p.py`
  - `bin/execute_replay_engine_hook_guarded_28z.py`
  - `bin/execute_replay_engine_hook_guarded_28z_r2.py`
  - `bin/guarded_offline_replay_dry_run_adapter_28p_r2.py`
  - `bin/guarded_replay_core_candidate_signature_bridge_28y.py`
  - `bin/guarded_replay_core_execution_adapter_28x.py`
  - `bin/guarded_replay_engine_adapter_29c.py`
  - `bin/guarded_replay_engine_execute_dry_run_29g.py`
  - `bin/guarded_replay_engine_execute_retry_29ad.py`
  - `bin/materialize_offline_run_context_shim_29f.py`
  - `bin/materialize_replay_engine_context_objects_29e.py`
  - `bin/observe_only_offline_replay_dataset_candidate_materialize_28m.py`
  - `bin/observe_only_offline_replay_materialization_dry_run_28l.py`
  - `bin/observe_only_offline_replay_materialization_harness_28k.py`
  - `bin/prepare_guarded_offline_replay_dry_run_contract_28o.py`

### bin/research_gate/

- planned_count: 4

  - `bin/dhan_closed_market_feeds_features_check.py`
  - `bin/lfeed.sh`
  - `bin/mfeed.sh`
  - `bin/phealth_safe.py`

### bin/unclassified_review_required/

- planned_count: 7

  - `bin/check_broker_token.py`
  - `bin/dhan_mcx_option_probe.py`
  - `bin/ensure_zerodha_shared_token.py`
  - `bin/export_session_artifacts.py`
  - `bin/feed_depth_witness.py`
  - `bin/predischeck.py`
  - `bin/top20.sh`

## Migration Rule

Do not move files directly.

Future migration must happen in stages:

1. Create target folders.
2. Move a small low-risk group first, preferably proof-only scripts.
3. Leave compatibility wrappers in old paths if any external calls exist.
4. Run compile/import/static path checks.
5. Write proof JSON and milestone.
6. Only then continue to next group.

Recommended first migration batch:

- proof-only scripts with no runtime-start flags
- no controlled paper scripts
- no broker/order scripts
- no runtime wrapper scripts

