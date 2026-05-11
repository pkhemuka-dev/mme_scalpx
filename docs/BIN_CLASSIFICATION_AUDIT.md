# MME-ScalpX Bin Classification Audit

Generated: 2026-05-11T23:11:07.606053

## Safety

- No files moved.
- No files deleted.
- No services started.
- No broker calls.
- No Redis writes.
- No paper/live enablement.

## Kind Counts

- controlled_paper: 7
- diagnostic: 8
- observe_only: 10
- patch: 3
- proof: 296
- replay: 40
- research_gate: 35
- runtime: 1
- unknown: 7

## Recommended Future Bucket Counts

- bin/controlled_paper/: 7
- bin/diagnostics/: 8
- bin/observe_only/: 10
- bin/patches/: 3
- bin/proofs/: 296
- bin/replay/: 40
- bin/research_gate/: 35
- bin/runtime/: 1
- bin/unclassified_review_required/: 7

## Review Required

- unknown_items: 7
- high_review_items: 343

## Unknown Items

- `bin/check_broker_token.py`
- `bin/dhan_mcx_option_probe.py`
- `bin/ensure_zerodha_shared_token.py`
- `bin/export_session_artifacts.py`
- `bin/feed_depth_witness.py`
- `bin/predischeck.py`
- `bin/top20.sh`

## High Review Items

- `bin/__pycache__/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.cpython-310.pyc` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/__pycache__/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.cpython-310.pyc` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/__pycache__/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.cpython-310.pyc` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/__pycache__/proof_batch26o23_j_post_repair_controlled_paper_observation.cpython-310.pyc` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/__pycache__/run_batch26o11_controlled_paper_monitor.cpython-310.pyc` — ORDER_MENTION, REDIS_MENTION
- `bin/__pycache__/start_batch26o10_controlled_paper.cpython-310.pyc` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/__pycache__/start_controlled_paper_runtime_chain.cpython-310.pyc` — RUNTIME_START_MENTION
- `bin/_batch25v_market_observation_common.py` — REDIS_MENTION
- `bin/_final_static_proof_helpers.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/actual_replay_engine_callable_adapter_28t.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/actual_replay_engine_module_adapter_28r.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/audit_dhan_context_completeness_25v.py` — BROKER_MENTION, REDIS_MENTION
- `bin/audit_guarded_replay_engine_runtime_gap_29h.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/audit_recorded_live_data_clean_inventory.py` — BROKER_MENTION
- `bin/audit_recorded_live_replay_readiness.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/audit_session_exports_schema.py` — BROKER_MENTION
- `bin/batch26m_enable_controlled_paper_from_25v25w.sh` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/batch26o2_deep_blocker_analysis.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/batch26o8a_after_market_closure_audit.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/build_proof_bundle.py` — SYSTEMD_MENTION
- `bin/check_broker_token.py` — UNKNOWN_KIND
- `bin/dhan_closed_market_feeds_features_check.py` — BROKER_MENTION
- `bin/dhan_mcx_option_probe.py` — BROKER_MENTION
- `bin/dhan_nifty_capability_audit.py` — BROKER_MENTION
- `bin/ensure_zerodha_shared_token.py` — BROKER_MENTION
- `bin/execute_guarded_offline_replay_dry_run_28p.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/execute_replay_engine_hook_guarded_28z.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/execute_replay_engine_hook_guarded_28z_r2.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/export_runtime_truth_evidence.py` — BROKER_MENTION, SYSTEMD_MENTION, RUNTIME_START_MENTION
- `bin/export_session_artifacts.py` — REDIS_MENTION
- `bin/feed_depth_witness.py` — ORDER_MENTION
- `bin/getfile` — BROKER_MENTION, REDIS_MENTION
- `bin/guarded_offline_replay_dry_run_adapter_28p_r2.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/guarded_replay_core_candidate_signature_bridge_28y.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/guarded_replay_core_execution_adapter_28x.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/guarded_replay_engine_adapter_29c.py` — BROKER_MENTION, REDIS_MENTION
- `bin/guarded_replay_engine_execute_dry_run_29g.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/guarded_replay_engine_execute_retry_29ad.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/lfeed.sh` — BROKER_MENTION, ORDER_MENTION
- `bin/live_session_forensics_readonly.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/live_signal_forensics_observer.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/materialize_offline_run_context_shim_29f.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/materialize_replay_engine_context_objects_29e.py` — BROKER_MENTION, REDIS_MENTION
- `bin/mfeed.sh` — BROKER_MENTION
- `bin/mme_live_observer.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/observe_only_live_evidence_collect.py` — BROKER_MENTION, REDIS_MENTION
- `bin/observe_only_market_session_capture_execute.py` — BROKER_MENTION, REDIS_MENTION
- `bin/observe_only_offline_replay_dataset_candidate_materialize_28m.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/observe_only_offline_replay_materialization_dry_run_28l.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/observe_only_offline_replay_materialization_harness_28k.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/observe_strategy_activation_report_live.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/patch_batch26b_execution_hard_arming_guard_thin.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/patch_batch26c_risk_controlled_paper_veto.py` — ORDER_MENTION, REDIS_MENTION
- `bin/patch_batch26d_strategy_leaf_required_surface_failclosed.py` — REDIS_MENTION
- `bin/phealth_safe.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/post_market_session_forensics.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/predischeck.py` — REDIS_MENTION
- `bin/prepair_safe.py` — REDIS_MENTION, RUNTIME_START_MENTION
- `bin/prepare_guarded_offline_replay_dry_run_contract_28o.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_5family_integration_master.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, SYSTEMD_MENTION, RUNTIME_START_MENTION
- `bin/proof_actual_replay_engine_integration_preflight_28q.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_aftermarket_full_replay_dry_run.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_aftermarket_historical_replay_readiness.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_aftermarket_strong_replay_sample.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_batch26a_current_repo_truth.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26b_execution_hard_arming_guard_thin.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26d_strategy_leaf_required_surface_failclosed.py` — REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26k_controlled_paper_prestart_readiness.py` — BROKER_MENTION, ORDER_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o13_activation_bridge_audit.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o14_controlled_activation_bridge.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o15_activation_candidate_surface_audit.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16_consumer_view_mapping_repair.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.py` — BROKER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.py` — BROKER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.py` — BROKER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16d_selected_option_classic_provider_readiness.py` — BROKER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16f_selected_option_source_to_feature_mapping.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16g_selected_option_provider_data_quality_tradability.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16h_final_data_valid_composition.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o16h_r2_persistent_final_composition.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o17_activation_candidate_extraction.py` — REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o17a_selected_option_common_abi_sanitizer.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o17b_common_parent_abi_sanitizer.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o17b_r2_common_abi_proof_correction.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o18_lightweight_controlled_paper_preflight.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o19_lightweight_controlled_paper_runtime.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o1_recovery_singleton_baseline.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_controlled_paper_extended_observation.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r2_bounded_short_observation.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3_corrected_bounded_observation.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3a_persistent_features_abi_publish_repair.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3b_corrected_bounded_observation.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3c_runtime_data_validity_source_audit.py` — REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3d_consumer_view_validity_semantics.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3d_r1_consumer_view_semantics_wrapper_repair.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3d_r2_source_publish_repair.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3d_r2a_structural_valid_source_field.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3f_persisted_features_publish_route_classifier.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3g_corrected_r3e_proof_parser.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o20r_recovery_after_terminated_o20.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o21_controlled_paper_promotion_readiness.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o21r_post_o21_orphan_cleanup.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_controlled_paper_longer_observation_plan.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r2_controlled_paper_plan_proof_correction.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r3_controlled_paper_static_gate_proof.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o22a_o20r2_o22_proof_chain_consistency.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_a_r1_session_completion_safety_readback.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_b_controlled_paper_evidence_review.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_b_r1_controlled_pid_cleanup_readback.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_b_r2_evidence_review_correction.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_c_r1_completion_safety_readback.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_d_second_session_evidence_review.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_e_no_candidate_root_cause_review.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_f_r2_disk_recovery_backup_policy.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_f_r4_prior_proof_loader_correction.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_g_narrow_bridge_diagnostic.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_h_narrow_bridge_repair.py` — ORDER_MENTION, REDIS_MENTION
- `bin/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_i_static_oneshot_bridge_proof.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_j_post_repair_controlled_paper_observation.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_k_post_repair_evidence_review.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_l_multi_strategy_signal_opportunity_audit.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_m_validate_mist_put_single_scope.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_n_corrected_opportunity_parser_deeper_sampler.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_o_r2_interrupted_recovery_readback.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_o_r3_clean_rerun_readonly_sampler.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o23_o_r5_nameerror_recovery_no_stream_growth_freeze.py` — ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o5_live_key_topology.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o7_controlled_runtime_start_preflight.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_batch26o9_controlled_paper_preflight.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_config_runtime_truth.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_contract_field_registry.py` — BROKER_MENTION, ORDER_MENTION
- `bin/proof_controlled_paper_runtime_wiring.py` — BROKER_MENTION, ORDER_MENTION, RUNTIME_START_MENTION
- `bin/proof_core_codec_transport.py` — ORDER_MENTION
- `bin/proof_core_infra_batch18_freeze.py` — REDIS_MENTION, RUNTIME_START_MENTION
- `bin/proof_dhan_context_adapter_ladder_payload.py` — BROKER_MENTION
- `bin/proof_dhan_context_quality.py` — BROKER_MENTION
- `bin/proof_dhan_execution_fallback_policy.py` — BROKER_MENTION, ORDER_MENTION, REDIS_MENTION
- `bin/proof_dhan_oi_ladder_persistence.py` — BROKER_MENTION, REDIS_MENTION

## Migration Rule

Do not move bin scripts until a separate compatibility-wrapper migration patch proves all call paths.
