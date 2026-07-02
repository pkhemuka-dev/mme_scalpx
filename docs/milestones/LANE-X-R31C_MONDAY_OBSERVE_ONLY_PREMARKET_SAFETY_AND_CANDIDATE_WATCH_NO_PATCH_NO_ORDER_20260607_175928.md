# LANE-X-R31C_MONDAY_OBSERVE_ONLY_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER_20260607_175928
2026-06-07T17:59:28+05:30

LAW=PREMARKET_AUDIT_ONLY_NO_PATCH_NO_START_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior handoff proof
R31B=run/proofs/LANE-X-R31B_ACCEPT_LANE_B_WAIT_STATE_AND_MONDAY_CANDIDATE_POSITIVE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_155806.json
{
  "tag": "LANE-X-R31B_ACCEPT_LANE_B_WAIT_STATE_AND_MONDAY_CANDIDATE_POSITIVE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_155806",
  "classification": "PASS_LANE_X_R31B_LANE_B_WAIT_STATE_ACCEPTED_MONDAY_CANDIDATE_POSITIVE_PLAN_READY",
  "patch_applied": false,
  "started_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "lane_b_wait_state_accepted": true,
  "next_lane_x_batch": "LANE-X-R31C_MONDAY_OBSERVE_ONLY_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_NO_PATCH_NO_ORDER",
  "report": "run/audits/LANE-X-R31B_ACCEPT_LANE_B_WAIT_STATE_AND_MONDAY_CANDIDATE_POSITIVE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_155806_report.md"
}

## Safety preflight
ACTIVE_RUNTIME_PROCESSES:
NONE

ORDER_RISK_EXECUTION_STREAM_SAFETY:
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Current git status
 M app/mme_scalpx/ops_dashboard/server.py
 M app/mme_scalpx/services/feature_family/misb_surface.py
 M app/mme_scalpx/services/features.py
 M data/instruments/nfo_instruments.csv
?? bin/lane_x_shadow_near_candidate_observer.py
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_203023.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027.md
?? docs/milestones/B4-R5P-V1_MICRO_SHELF_PATCH_VERIFY_FINALIZE_NO_START_NO_ORDER_20260603_234959.md
?? docs/milestones/B4-R5P-V2_MICRO_SHELF_CONTRACT_PASSTHROUGH_SELFTEST_NO_START_NO_ORDER_20260603_235105.md
?? docs/milestones/B4-R5P-V3_MISB_SHELF_CONSUMER_SELFTEST_NO_START_NO_ORDER_20260603_235205.md
?? docs/milestones/LANE-B-R1A_RECOVER_R1_SURFACE_AUDIT_ARTIFACTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_121122.md
?? docs/milestones/LANE-B-R1_REPLAY_SURFACE_BASELINE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_120747.md
?? docs/milestones/LANE-B-R2A_REPLAY_DATASET_AND_PREVIOUS_RUN_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_134930.md
?? docs/milestones/LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114.md
?? docs/milestones/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738.md
?? docs/milestones/LANE-B-R2D_R2C_REPLAY_ARTIFACT_SHAPE_COUNT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140338.md
?? docs/milestones/LANE-B-R2E1_FINGERPRINT_PROVENANCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141109.md
?? docs/milestones/LANE-B-R2E_COMPARE_R2C_VS_B3R61D_REPLAY_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140836.md
?? docs/milestones/LANE-B-R2F-R1_INTERRUPTED_REPLAY_FREEZE_SIDE_EFFECT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_verify_interrupted_r2f_heredoc_created_no_replay_no_order_no_side_effect_20260607_141459.md
?? docs/milestones/LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428.md
?? docs/milestones/LANE-B-R2F_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_r1_to_r2e1_a7_single_day_replay_reproducibility_with_fingerprint_caveat_20260607_141320.md
?? docs/milestones/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805.md
?? docs/milestones/LANE-B-R3B_FILL_MODEL_ABI_AND_R4_COMMAND_CORRECTION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141930.md
?? docs/milestones/LANE-B-R3_RISK_EXECUTION_SHADOW_PNL_READINESS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141540.md
?? docs/milestones/LANE-B-R4A2_CORRECTED_SHADOW_PNL_NO_TRADE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143017.md
?? docs/milestones/LANE-B-R4A_SHADOW_PNL_NO_TRADE_ARTIFACT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_142909.md
?? docs/milestones/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249.md
?? docs/milestones/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143301.md
?? docs/milestones/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143419.md
?? docs/milestones/LANE-B-R5B_BASELINE_VS_SHADOW_PATCH_IMPACT_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143653.md
?? docs/milestones/LANE-B-R5C_BASELINE_SHADOW_DRY_RUN_PACKAGE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143758.md
?? docs/milestones/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907.md
?? docs/milestones/LANE-B-R5E_COMPARE_BASELINE_SHADOW_PATCH_IMPACT_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154016.md
?? docs/milestones/LANE-B-R5F_FINAL_PATCH_IMPACT_AND_PNL_ROUTE_DECISION_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154208.md
?? docs/milestones/LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108.md
?? docs/milestones/LANE-B-R6A_STRATEGY_PNL_WAIT_STATE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154637.md
?? docs/milestones/LANE-B-R6B_WAIT_STATE_HANDOFF_BUNDLE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154920.md
?? docs/milestones/LANE-B-R6_CANDIDATE_POSITIVE_DATASET_ADMISSION_GATE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154426.md
?? docs/milestones/LANE-X-CLOSE-R3_corrected_pseal_completion_finalizer_20260604_152311.md
?? docs/milestones/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203209.md
?? docs/milestones/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203215.md
?? docs/milestones/LANE-X-DASH-R1_dashboard_lane_evidence_bundle_no_patch_no_order_20260604_230829.md
?? docs/milestones/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059.md
?? docs/milestones/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421.md
?? docs/milestones/LANE-X-DASH-R2B-TINY-SEAL_STATIC_OBSERVE_PANEL_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_seal_existing_lx_tiny_source_markers_compile_import_ast_safety_20260604_232058.md
?? docs/milestones/LANE-X-DASH-R2C_RUNTIME_SEAL_LX_TINY_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER_restart_dashboard_only_and_seal_running_lane_x_observe_page_markers_20260604_232202.md
?? docs/milestones/LANE-X-PDISK-R1_safe_cleanup_inventory_no_delete_20260604_210232.md
?? docs/milestones/LANE-X-PDISK-R2_explicit_cleanup_plan_no_delete_20260604_210418.md
?? docs/milestones/LANE-X-R12_day4_evidence_index_no_patch_no_order_20260604_203314.md
?? docs/milestones/LANE-X-R13B_sealed_data_integrity_finalizer_exclude_self_sha_20260604_203618.md
?? docs/milestones/LANE-X-R13_sealed_data_integrity_audit_no_patch_no_replay_no_order_20260604_203422.md
?? docs/milestones/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712.md
?? docs/milestones/LANE-X-R15_misb_shelf_width_distribution_audit_no_patch_no_replay_no_order_20260604_203827.md
?? docs/milestones/LANE-X-R16_mist_response_futures_impulse_audit_no_patch_no_replay_no_order_20260604_204031.md
?? docs/milestones/LANE-X-R17B_compact_snapshot_sync_view_data_invalid_finalizer_20260604_205244.md
?? docs/milestones/LANE-X-R17_snapshot_sync_view_data_invalid_audit_no_patch_no_replay_no_order_20260604_204256.md
?? docs/milestones/LANE-X-R18_dhan_miso_unavailable_audit_no_patch_no_replay_no_order_20260604_205403.md
?? docs/milestones/LANE-X-R19A_helper_source_locator_no_patch_no_order_20260604_205537.md
?? docs/milestones/LANE-X-R19B_pcheck_disk_emoji_helper_patch_no_order_20260604_205659.md
?? docs/milestones/LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815.md
?? docs/milestones/LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936.md
?? docs/milestones/LANE-X-R20_day4_consolidated_milestone_and_tomorrow_plan_no_patch_no_order_20260604_210132.md
?? docs/milestones/LANE-X-R21_family_strategy_source_review_bundle_no_patch_no_order_20260604_211329.md
?? docs/milestones/LANE-X-R22A_mist_micro_option_response_source_seam_audit_no_patch_no_order_20260604_211933.md
?? docs/milestones/LANE-X-R22B-DIAG_micro_option_response_context_no_patch_no_order_20260604_224928.md
?? docs/milestones/LANE-X-R22B-REPAIR_micro_option_response_return_path_repair_no_start_no_order_20260604_225050.md
?? docs/milestones/LANE-X-R22B_micro_option_response_producer_patch_no_start_no_order_20260604_224759.md
?? docs/milestones/LANE-X-R22C-R2_corrected_mist_branch_consumer_micro_response_selftest_no_start_no_order_20260604_225319.md
?? docs/milestones/LANE-X-R22C_mist_consumer_micro_response_selftest_no_start_no_order_20260604_225141.md
?? docs/milestones/LANE-X-R22D_micro_option_response_patch_finalizer_tomorrow_live_validation_no_start_no_order_20260604_225437.md
?? docs/milestones/LANE-X-R23_post_r22_micro_response_evidence_bundle_no_patch_no_order_20260604_225905.md
?? docs/milestones/LANE-X-R24A_opportunity_expansion_source_seam_audit_no_patch_no_order_20260604_230020.md
?? docs/milestones/LANE-X-R24B_shadow_near_candidate_observer_helper_no_production_candidate_no_order_20260604_230313.md
?? docs/milestones/LANE-X-R24C_post_r24b_shadow_near_candidate_finalizer_no_patch_no_order_20260604_230456.md
?? docs/milestones/LANE-X-R25A_friday_premarket_r22_r24b_readiness_no_start_no_order_20260605_091006.md
?? docs/milestones/LANE-X-R25A_friday_premarket_r22_r24b_readiness_no_start_no_order_20260605_091015.md
?? docs/milestones/LANE-X-R25B-WAIT_post_open_health_recheck_no_start_no_stop_no_order_20260605_091425.md
?? docs/milestones/LANE-X-R25B-WAIT_post_open_health_recheck_no_start_no_stop_no_order_20260605_091611.md
?? docs/milestones/LANE-X-R25B_friday_observe_only_start_or_reuse_no_patch_no_order_20260605_091243.md
?? docs/milestones/LANE-X-R25C_features_strategy_stale_log_triage_no_start_no_stop_no_patch_no_order_20260605_091725.md
?? docs/milestones/LANE-X-R25D_r22b_wrapper_side_kwarg_hotfix_no_start_no_stop_no_order_20260605_091906.md
?? docs/milestones/LANE-X-R25E_refresh_features_strategy_after_r25d_hotfix_no_feeds_no_order_20260605_092014.md
?? docs/milestones/LANE-X-R25F_recover_missing_features_strategy_after_r25e_no_kill_no_feeds_no_order_20260605_092129.md
?? docs/milestones/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342.md
?? docs/milestones/LANE-X-R25H_feature_consumer_view_provider_ready_inspector_no_patch_no_order_20260605_092458.md
?? docs/milestones/LANE-X-R25J_rolling_r22_snapshot_tradability_sampler_no_patch_no_order_20260605_093000.md
?? docs/milestones/LANE-X-R25K_futures_source_inventory_after_fut_missing_pcheck_no_patch_no_order_20260605_095301.md
?? docs/milestones/LANE-X-R25L_option_side_role_consistency_sampler_no_patch_no_order_20260605_095512.md
?? docs/milestones/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_104251.md
?? docs/milestones/LANE-X-R25M_invalid_member_anomaly_clamped_sampler_no_patch_no_order_20260605_101117.md
?? docs/milestones/LANE-X-R25N_shadow_opportunity_snapshot_freeze_no_patch_no_order_20260605_134052.md
?? docs/milestones/LANE-X-R25N_valid_frame_family_opportunity_sampler_no_patch_no_order_20260605_110051.md
?? docs/milestones/LANE-X-R25O_candidate_promotion_gap_inspector_no_patch_no_order_20260605_110846.md
?? docs/milestones/LANE-X-R25O_day5_pseal_completion_finalizer_no_patch_no_order_20260605_152150.md
?? docs/milestones/LANE-X-R25P_day5_compact_evidence_bundle_no_patch_no_order_20260605_152449.md
?? docs/milestones/LANE-X-R25P_mist_futures_impulse_gap_inspector_no_patch_no_order_20260605_111037.md
?? docs/milestones/LANE-X-R25R_futures_kinetic_primitive_gap_sampler_no_patch_no_order_20260605_112133.md
?? docs/milestones/LANE-X-R25T_readonly_hypothetical_futures_kinetics_from_raw_ticks_no_patch_no_order_20260605_113952.md
?? docs/milestones/LANE-X-R26A_day5_bundle_root_cause_freeze_no_patch_no_order_20260607_112913.md
?? docs/milestones/LANE-X-R26B_micro_futures_kinetics_producer_patch_no_start_no_order_20260607_113211.md
?? docs/milestones/LANE-X-R26C_micro_futures_kinetics_mist_consumer_selftest_no_patch_no_order_20260607_113339.md
?? docs/milestones/LANE-X-R26D-R2_corrected_redisraw_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113823.md
?? docs/milestones/LANE-X-R26D-R3_preserve_blank_values_redisraw_futures_kinetics_validator_no_patch_no_order_20260607_114851.md
?? docs/milestones/LANE-X-R26D-R4_chronological_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_115028.md
?? docs/milestones/LANE-X-R26D_day5_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113438.md
?? docs/milestones/LANE-X-R26E_micro_futures_kinetics_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_115137.md
?? docs/milestones/LANE-X-R26F_micro_futures_kinetics_chain_evidence_bundle_no_patch_no_order_20260607_115245.md
?? docs/milestones/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657.md
?? docs/milestones/LANE-X-R27B_misb_shelf_width_scale_window_audit_no_patch_no_order_20260607_115937.md
?? docs/milestones/LANE-X-R27C_misb_shelf_threshold_scenario_quality_audit_no_patch_no_order_20260607_120106.md
?? docs/milestones/LANE-X-R27D_misb_current_inclusive_shelf_reference_audit_no_patch_no_order_20260607_120243.md
?? docs/milestones/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500.md
?? docs/milestones/LANE-X-R27F_sealed_prior_shelf_ref_contract_passthrough_validator_no_patch_no_order_20260607_120622.md
?? docs/milestones/LANE-X-R27G_misb_prior_shelf_ref_contract_passthrough_patch_no_start_no_order_20260607_120850.md
?? docs/milestones/LANE-X-R27H_rerun_sealed_prior_ref_contract_passthrough_validator_no_patch_no_order_20260607_121008.md
?? docs/milestones/LANE-X-R27I_misb_prior_shelf_ref_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_121138.md
?? docs/milestones/LANE-X-R27J_misb_prior_shelf_ref_chain_evidence_bundle_no_patch_no_order_20260607_121241.md
?? docs/milestones/LANE-X-R28A_weekend_consolidated_finalizer_monday_observe_checklist_no_patch_no_order_20260607_121432.md
?? docs/milestones/LANE-X-R28B_final_weekend_observe_ready_evidence_bundle_no_patch_no_order_20260607_121600.md
?? docs/milestones/LANE-X-R29A-R4_PREMARKET_RECONNECT_MINI_AUDIT_NO_PATCH_NO_START_NO_ORDER_after_ssh_drop_verify_no_side_effect_source_safety_r28b_ready_20260607_135037.md
?? docs/milestones/LANE-X-R29B-R1_INTERRUPTED_SUNDAY_START_ATTEMPT_SIDE_EFFECT_AUDIT_NO_PATCH_NO_START_NO_ORDER_verify_r29b_interrupted_paste_did_not_start_risk_execution_or_order_20260607_135857.md
?? docs/milestones/LANE-X-R29B-R2_MINIMAL_MONDAY_OBSERVE_ONLY_START_REUSE_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_minimal_helper_based_start_reuse_after_r29a_pass_20260607_135950.md
?? docs/milestones/LANE-X-R30A_FAMILY_MICROSTRUCTURE_COVERAGE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_mist_misb_misc_misr_miso_required_microstructure_surfaces_and_contract_passthrough_20260607_140857.md
?? docs/milestones/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044.md
?? docs/milestones/LANE-X-R30D_PROVIDER_RUNTIME_KEY_CONTRACT_ALIGNMENT_AUDIT_NO_PATCH_NO_START_NO_ORDER_compare_names_provider_runtime_publishers_readers_pcheck_expected_redis_keys_20260607_141254.md
?? docs/milestones/LANE-X-R31A-R1_INTERRUPTED_SHADOW_PNL_FEASIBILITY_SIDE_EFFECT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_verify_interrupted_r31a_created_no_replay_no_order_no_side_effect_20260607_143923.md
?? docs/milestones/LANE-X-R31A-R2_REPLAY_PROC_IDENTIFICATION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_identify_replay_proc_one_from_r31a_r1_before_any_next_action_20260607_144010.md
?? docs/milestones/LANE-X-R31A-R3_WAIT_ON_ACTIVE_LANE_B_REPLAY_READONLY_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_monitor_active_lane_b_r5d_replay_before_resuming_friday_shadow_pnl_feasibility_20260607_144052.md
?? docs/milestones/LANE-X-R31A-R4_R5D_SHADOW_RESULT_ARTIFACT_SUMMARY_NO_PATCH_NO_REPLAY_NO_ORDER_read_completed_lane_b_r5d_baseline_shadow_outputs_for_shadow_pnl_availability_20260607_154229.md
?? docs/milestones/LANE-X-R31A-R4_R5D_SHADOW_RESULT_ARTIFACT_SUMMARY_NO_PATCH_NO_REPLAY_NO_ORDER_read_completed_lane_b_r5d_baseline_shadow_outputs_for_shadow_pnl_availability_20260607_154433.md
?? docs/milestones/LANE-X-R31A-R5_EXTRACT_R5D_SHADOW_PNL_NUMBERS_NO_PATCH_NO_REPLAY_NO_ORDER_extract_baseline_vs_shadow_trade_pnl_economics_from_completed_r5d_artifacts_20260607_154615.md
?? docs/milestones/LANE-X-R31A-R6_ZERO_CANDIDATE_BLOCKER_DECOMPOSITION_NO_PATCH_NO_REPLAY_NO_ORDER_explain_why_r5d_baseline_and_shadow_generated_zero_candidates_zero_trades_null_pnl_20260607_155734.md
?? docs/milestones/LANE-X-R31A_FRIDAY_SHADOW_PNL_FEASIBILITY_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_friday_capture_fut_opt_feature_decision_timing_for_shadow_pnl_reconstruction_20260607_142215.md
?? docs/milestones/LANE-X-R31B_ACCEPT_LANE_B_WAIT_STATE_AND_MONDAY_CANDIDATE_POSITIVE_PLAN_NO_PATCH_NO_START_NO_ORDER_20260607_155806.md
?? docs/runbooks/LANE-B-R1_REPLAY_SURFACE_BASELINE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_120747_runbook.md
?? docs/runbooks/LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114_runbook.md
?? docs/runbooks/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738_runbook.md
?? docs/runbooks/LANE-B-R2D_R2C_REPLAY_ARTIFACT_SHAPE_COUNT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140338_runbook.md
?? docs/runbooks/LANE-B-R2E1_FINGERPRINT_PROVENANCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141109_runbook.md
?? docs/runbooks/LANE-B-R2E_COMPARE_R2C_VS_B3R61D_REPLAY_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140836_runbook.md
?? docs/runbooks/LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428_runbook.md
?? docs/runbooks/LANE-B-R2F_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_r1_to_r2e1_a7_single_day_replay_reproducibility_with_fingerprint_caveat_20260607_141320_runbook.md
?? docs/runbooks/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805_runbook.md
?? docs/runbooks/LANE-B-R3B_FILL_MODEL_ABI_AND_R4_COMMAND_CORRECTION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141930_runbook.md
?? docs/runbooks/LANE-B-R3_RISK_EXECUTION_SHADOW_PNL_READINESS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141540_runbook.md
?? docs/runbooks/LANE-B-R4A2_CORRECTED_SHADOW_PNL_NO_TRADE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143017_runbook.md
?? docs/runbooks/LANE-B-R4A_SHADOW_PNL_NO_TRADE_ARTIFACT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_142909_runbook.md
?? docs/runbooks/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249_runbook.md
?? docs/runbooks/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143301_runbook.md
?? docs/runbooks/LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143419_runbook.md
?? docs/runbooks/LANE-B-R5B_BASELINE_VS_SHADOW_PATCH_IMPACT_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143653_runbook.md
?? docs/runbooks/LANE-B-R5C_BASELINE_SHADOW_DRY_RUN_PACKAGE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143758_runbook.md
?? docs/runbooks/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907_runbook.md
?? docs/runbooks/LANE-B-R5E_COMPARE_BASELINE_SHADOW_PATCH_IMPACT_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154016_runbook.md
?? docs/runbooks/LANE-B-R5F_FINAL_PATCH_IMPACT_AND_PNL_ROUTE_DECISION_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154208_runbook.md
?? docs/runbooks/LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108_runbook.md
?? docs/runbooks/LANE-B-R6A_STRATEGY_PNL_WAIT_STATE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154637_runbook.md
?? docs/runbooks/LANE-B-R6B_WAIT_STATE_HANDOFF_BUNDLE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154920_runbook.md
?? docs/runbooks/LANE-B-R6_CANDIDATE_POSITIVE_DATASET_ADMISSION_GATE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154426_runbook.md

## Helper / observer availability
MISSING_HELPER pauto_start
MISSING_HELPER pauto_status
FOUND_HELPER pcheck
MISSING_HELPER pseal
FOUND_HELPER pfeeds
FOUND_HELPER pstack
FOUND_HELPER pfeedcheck
FOUND_HELPER pstackcheck

FOUND bin/lane_x_shadow_near_candidate_observer.py
FOUND app/mme_scalpx/services/features.py
FOUND app/mme_scalpx/services/strategy.py
FOUND app/mme_scalpx/services/feature_family/misb_surface.py
FOUND app/mme_scalpx/services/strategy_family
FOUND app/mme_scalpx/core/names.py

## Compile smoke for Monday observe readiness
COMPILE_RC=0

## Source markers for Monday candidate-positive watch
app/mme_scalpx/services/features.py:3187:            "provider_ready_classic": classic_mode != RUNTIME_DISABLED,
app/mme_scalpx/services/features.py:3460:                "provider_ready_classic": bool(provider.get("classic_runtime_mode") != RUNTIME_DISABLED),
app/mme_scalpx/services/features.py:4200:    provider_ready_classic = _safe_bool(stage_flags.get("provider_ready_classic"), False)
app/mme_scalpx/services/features.py:4203:    safe_to_consume = bool(
app/mme_scalpx/services/features.py:4222:        "safe_to_consume": safe_to_consume,
app/mme_scalpx/services/features.py:4223:        "hold_only": True,
app/mme_scalpx/services/features.py:4228:        "provider_ready_classic": provider_ready_classic,
app/mme_scalpx/services/features.py:4961:    provider_ready_classic = bool(
app/mme_scalpx/services/features.py:4986:            and provider_ready_classic
app/mme_scalpx/services/features.py:4992:        out["data_valid"] and not snapshot_sync_valid and provider_ready_classic
app/mme_scalpx/services/features.py:4997:    out["provider_ready_classic"] = provider_ready_classic
app/mme_scalpx/services/features.py:5469:    out["provider_ready_classic"] = classic_ready
app/mme_scalpx/services/features.py:5705:    out["provider_ready_classic"] = classic_ready
app/mme_scalpx/services/features.py:6994:            flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:7007:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7019:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7274:            flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:7288:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7299:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7948:# - ABI-clean 10-branch consumer view is data_valid=True and safe_to_consume=True.
app/mme_scalpx/services/features.py:8003:            out["safe_to_consume"] = True
app/mme_scalpx/services/features.py:8005:            out["hold_only"] = True
app/mme_scalpx/services/features.py:8093:# consumer_view_json.data_valid=false / safe_to_consume=false / structural_valid=null.
app/mme_scalpx/services/features.py:8172:            out["safe_to_consume"] = True
app/mme_scalpx/services/features.py:8174:            out["hold_only"] = True
app/mme_scalpx/services/features.py:8295:        out["safe_to_consume"] = True
app/mme_scalpx/services/features.py:8298:        out["hold_only"] = True
app/mme_scalpx/services/features.py:8339:# R2 proved data_valid=true and safe_to_consume=true, but structural_valid was
app/mme_scalpx/services/features.py:8357:    if complete and out.get("data_valid") is True and out.get("safe_to_consume") is True:
app/mme_scalpx/services/features.py:8430:                if _batch26o20r3d_r2b_payload_structural_safe(cv2) and cv2.get("data_valid") is True and cv2.get("safe_to_consume") is True:
app/mme_scalpx/services/features.py:8663:        provider["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8667:        flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8673:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:8895:            provider["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8897:            flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8903:                and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:8927:# B4_R5P_MICRO_SHELF_PRODUCER_PATCH_BEGIN
app/mme_scalpx/services/features.py:8940:_B4_R5P_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface
app/mme_scalpx/services/features.py:8941:_B4_R5P_PREV_CONTRACT_FUTURES_BLOCK = FeatureEngine._contract_futures_block
app/mme_scalpx/services/features.py:8943:_B4_R5P_MICRO_SHELF_WINDOW_NS = 45_000_000_000
app/mme_scalpx/services/features.py:8944:_B4_R5P_MICRO_SHELF_MAX_SAMPLES = 96
app/mme_scalpx/services/features.py:8945:_B4_R5P_MICRO_SHELF_MIN_SNAPSHOTS = 3
app/mme_scalpx/services/features.py:9037:    cutoff = event_ns - _B4_R5P_MICRO_SHELF_WINDOW_NS if event_ns > 0 else 0
app/mme_scalpx/services/features.py:9043:    samples = samples[-_B4_R5P_MICRO_SHELF_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9048:    out.setdefault("breakout_shelf_window_seconds", int(_B4_R5P_MICRO_SHELF_WINDOW_NS / 1_000_000_000))
app/mme_scalpx/services/features.py:9054:    if count < _B4_R5P_MICRO_SHELF_MIN_SNAPSHOTS:
app/mme_scalpx/services/features.py:9100:    surface = _B4_R5P_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9110:    block = _B4_R5P_PREV_CONTRACT_FUTURES_BLOCK(self, surface)
app/mme_scalpx/services/features.py:9155:# B4_R5P_MICRO_SHELF_PRODUCER_PATCH_END
app/mme_scalpx/services/features.py:9236:# LANE_X_R26B_MICRO_FUTURES_KINETICS_BEGIN
app/mme_scalpx/services/features.py:9252:_LANE_X_R26B_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface
app/mme_scalpx/services/features.py:9253:_LANE_X_R26B_PREV_CONTRACT_FUTURES_BLOCK = FeatureEngine._contract_futures_block
app/mme_scalpx/services/features.py:9255:_LANE_X_R26B_MAX_SAMPLES = 12
app/mme_scalpx/services/features.py:9256:_LANE_X_R26B_EVENT_RATE_BASELINE_PER_SEC = 0.20
app/mme_scalpx/services/features.py:9338:def _lane_x_r26b_micro_futures_kinetics(self, surface, *, role, provider_id):
app/mme_scalpx/services/features.py:9342:        out.setdefault("micro_futures_kinetics_source", "micro_futures_no_valid_price")
app/mme_scalpx/services/features.py:9343:        out.setdefault("micro_futures_kinetics_ready", False)
app/mme_scalpx/services/features.py:9359:    samples = samples[-_LANE_X_R26B_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9368:    out["micro_futures_kinetics_source"] = "micro_futures_kinetics"
app/mme_scalpx/services/features.py:9369:    out["micro_futures_kinetics_sample_count"] = sample_count
app/mme_scalpx/services/features.py:9372:        out["micro_futures_kinetics_ready"] = False
app/mme_scalpx/services/features.py:9394:    event_rate_norm = event_rate / max(_LANE_X_R26B_EVENT_RATE_BASELINE_PER_SEC, 1e-9)
app/mme_scalpx/services/features.py:9417:    out["micro_futures_kinetics_ready"] = True
app/mme_scalpx/services/features.py:9438:        surface = _LANE_X_R26B_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9447:        surface = _LANE_X_R26B_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9457:    return _lane_x_r26b_micro_futures_kinetics(
app/mme_scalpx/services/features.py:9466:    block = _LANE_X_R26B_PREV_CONTRACT_FUTURES_BLOCK(self, surface)
app/mme_scalpx/services/features.py:9480:        "micro_futures_kinetics_source",
app/mme_scalpx/services/features.py:9481:        "micro_futures_kinetics_ready",
app/mme_scalpx/services/features.py:9482:        "micro_futures_kinetics_sample_count",
app/mme_scalpx/services/features.py:9504:# LANE_X_R26B_MICRO_FUTURES_KINETICS_END
app/mme_scalpx/services/features.py:9506:# LANE_X_R27E_MISB_PRIOR_SHELF_REF_BEGIN
app/mme_scalpx/services/features.py:9518:# - breakout_shelf_prior_high / breakout_shelf_prior_low
app/mme_scalpx/services/features.py:9525:_LANE_X_R27E_PREV_FUTURES_SURFACE = FeatureEngine._futures_surface
app/mme_scalpx/services/features.py:9527:_LANE_X_R27E_WINDOW_NS = 45_000_000_000
app/mme_scalpx/services/features.py:9528:_LANE_X_R27E_MAX_SAMPLES = 96
app/mme_scalpx/services/features.py:9632:    cutoff = event_ns - _LANE_X_R27E_WINDOW_NS if event_ns else 0
app/mme_scalpx/services/features.py:9635:    samples = samples[-_LANE_X_R27E_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9652:                "breakout_shelf_prior_high": high,
app/mme_scalpx/services/features.py:9653:                "breakout_shelf_prior_low": low,
app/mme_scalpx/services/features.py:9654:                "breakout_shelf_prior_width": width,
app/mme_scalpx/services/features.py:9655:                "breakout_shelf_prior_width_pct": width_pct,
app/mme_scalpx/services/features.py:9656:                "breakout_shelf_prior_count": len(prices),
app/mme_scalpx/services/features.py:9662:        out = _LANE_X_R27E_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9671:        out = _LANE_X_R27E_PREV_FUTURES_SURFACE(
app/mme_scalpx/services/features.py:9692:        hist[key] = samples[-_LANE_X_R27E_MAX_SAMPLES:]
app/mme_scalpx/services/features.py:9703:# LANE_X_R27E_MISB_PRIOR_SHELF_REF_END
app/mme_scalpx/services/features.py:9705:# LANE_X_R27G_MISB_PRIOR_REF_CONTRACT_PASSTHROUGH_BEGIN
app/mme_scalpx/services/features.py:9714:_LANE_X_R27G_PREV_CONTRACT_FUTURES_BLOCK = FeatureEngine._contract_futures_block
app/mme_scalpx/services/features.py:9716:_LANE_X_R27G_PRIOR_REF_KEYS = (
app/mme_scalpx/services/features.py:9721:    "breakout_shelf_prior_high",
app/mme_scalpx/services/features.py:9722:    "breakout_shelf_prior_low",
app/mme_scalpx/services/features.py:9723:    "breakout_shelf_prior_width",
app/mme_scalpx/services/features.py:9724:    "breakout_shelf_prior_width_pct",
app/mme_scalpx/services/features.py:9725:    "breakout_shelf_prior_count",
app/mme_scalpx/services/features.py:9732:    block = _LANE_X_R27G_PREV_CONTRACT_FUTURES_BLOCK(self, surface)
app/mme_scalpx/services/features.py:9740:    for key in _LANE_X_R27G_PRIOR_REF_KEYS:
app/mme_scalpx/services/features.py:9749:# LANE_X_R27G_MISB_PRIOR_REF_CONTRACT_PASSTHROUGH_END
app/mme_scalpx/services/strategy.py:430:    if not _safe_bool(decision.get("hold_only"), False):
app/mme_scalpx/services/strategy.py:431:        raise StrategyBridgeError("strategy.py HOLD-only bridge requires hold_only=1")
app/mme_scalpx/services/strategy.py:595:    safe_to_consume: bool
app/mme_scalpx/services/strategy.py:596:    hold_only: bool
app/mme_scalpx/services/strategy.py:601:    provider_ready_classic: bool
app/mme_scalpx/services/strategy.py:619:            "safe_to_consume": self.safe_to_consume,
app/mme_scalpx/services/strategy.py:620:            "hold_only": self.hold_only,
app/mme_scalpx/services/strategy.py:625:            "provider_ready_classic": self.provider_ready_classic,
app/mme_scalpx/services/strategy.py:676:            allow_candidate_promotion=_r38r_controlled_paper_candidate_promotion_allowed(),
app/mme_scalpx/services/strategy.py:678:            require_hold_only_view=True,
app/mme_scalpx/services/strategy.py:679:            require_safe_to_consume=True,
app/mme_scalpx/services/strategy.py:801:        provider_ready_classic = _safe_bool(stage_flags.get("provider_ready_classic"), False)
app/mme_scalpx/services/strategy.py:804:        safe_to_consume = bool(
app/mme_scalpx/services/strategy.py:821:            safe_to_consume=safe_to_consume,
app/mme_scalpx/services/strategy.py:822:            hold_only=True,
app/mme_scalpx/services/strategy.py:824:            reason="hold_only_family_features_consumer_bridge",
app/mme_scalpx/services/strategy.py:827:            provider_ready_classic=provider_ready_classic,
app/mme_scalpx/services/strategy.py:895:            if _r38r_controlled_paper_candidate_promotion_allowed() and observed_safe_to_promote:
app/mme_scalpx/services/strategy.py:981:            "hold_only": 1,
app/mme_scalpx/services/strategy.py:998:            "safe_to_consume": int(view.safe_to_consume),
app/mme_scalpx/services/strategy.py:1001:            "provider_ready_classic": int(view.provider_ready_classic),
app/mme_scalpx/services/strategy.py:1010:                    "hold_only": True,
app/mme_scalpx/services/strategy.py:1348:        "strategy_publishes_hold_only": True,
app/mme_scalpx/services/strategy.py:1480:        if any(k in obj for k in ("data_valid", "safe_to_consume", "structural_valid")):
app/mme_scalpx/services/strategy.py:1517:    safe_to_consume = cv.get("safe_to_consume")
app/mme_scalpx/services/strategy.py:1526:            if safe_to_consume is None and "safe_to_consume" in nested:
app/mme_scalpx/services/strategy.py:1527:                safe_to_consume = nested.get("safe_to_consume")
app/mme_scalpx/services/strategy.py:1533:        "safe_to_consume": _o23h_boolish(safe_to_consume),
app/mme_scalpx/services/strategy.py:1537:            "safe_to_consume": safe_to_consume,
app/mme_scalpx/services/strategy.py:1544:    truth["all_valid"] = truth["data_valid"] and truth["safe_to_consume"] and truth["structural_valid"]
app/mme_scalpx/services/strategy.py:1625:    - only activates on the existing hold_only_family_features_consumer_bridge path;
app/mme_scalpx/services/strategy.py:1627:      safe_to_consume, and structural_valid;
app/mme_scalpx/services/strategy.py:1641:    if _r4r20m_reason == "hold_only_family_features_consumer_bridge":
app/mme_scalpx/services/strategy.py:1644:            "family_runtime_gate_reason": "global_gate_hold_only_family_features_consumer_bridge",
app/mme_scalpx/services/strategy.py:1658:                _r4r20m_meta.setdefault("family_runtime_gate_reason", "global_gate_hold_only_family_features_consumer_bridge")
app/mme_scalpx/services/strategy.py:1664:        if "hold_only_family_features_consumer_bridge" not in reason:
app/mme_scalpx/services/strategy.py:1702:            "safe_to_consume": True,
app/mme_scalpx/services/strategy.py:1844:def _r38r_controlled_paper_candidate_promotion_allowed():
app/mme_scalpx/services/feature_family/misb_surface.py:529:    # LANE_X_R27E_MISB_PRIOR_BREAKOUT_REF_BEGIN
app/mme_scalpx/services/feature_family/misb_surface.py:536:                "breakout_shelf_prior_high",
app/mme_scalpx/services/feature_family/misb_surface.py:547:                "breakout_shelf_prior_low",
app/mme_scalpx/services/feature_family/misb_surface.py:552:    # LANE_X_R27E_MISB_PRIOR_BREAKOUT_REF_END
bin/lane_x_shadow_near_candidate_observer.py:69:        return "shadow_strong_near_candidate"
bin/lane_x_shadow_near_candidate_observer.py:71:        return "shadow_medium_near_candidate"
bin/lane_x_shadow_near_candidate_observer.py:73:        return "shadow_weak_near_candidate"
bin/lane_x_shadow_near_candidate_observer.py:186:        "near_candidate_count": len(near),

## Monday observe-only candidate-watch objective
MONDAY_OBSERVE_OBJECTIVE:
  Start/reuse observe-only stack only after separate start approval.
  Do not start risk.
  Do not start execution.
  Do not enable paper/live.
  Do not place broker orders.
  Do not delete Redis or locks.
  Capture enough live observe-only data to determine whether candidate-positive evidence exists.

WATCH_FIELDS:
  - safe_to_consume
  - hold_only
  - data_valid
  - snapshot_sync_valid
  - provider_ready_classic
  - selected_option.tradability_ok
  - family_id
  - side
  - branch score / score gap / near_candidate
  - candidate
  - action
  - blocker_name
  - blocker_reason
  - economics_reason
  - MISB shelf_valid
  - breakout_shelf_prior_high
  - breakout_shelf_prior_low
  - MIST micro_futures_kinetics_ready
  - micro_futures_velocity_ratio
  - micro_futures_delta_3

LANE_B_RESUME_CONDITION:
  Resume Lane B only if a sealed observe-only dataset has candidate-positive evidence:
    - candidate_count > 0, or
    - strategy action other than HOLD, or
    - credible near-candidate evidence worth replay admission, or
    - execution_shadow_filled_count > 0 after offline replay.

CLASSIFICATION=PASS_LANE_X_R31C_PREMARKET_SAFETY_AND_CANDIDATE_WATCH_READY_FOR_OBSERVE_ONLY_START_REUSE
