# LANE-B-R5A_PATCH_IMPACT_REPLAY_ROUTE_PREFLIGHT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143301
2026-06-07T14:33:01+05:30

LAW=ROUTE_PREFLIGHT_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## R5 route proof
R5=run/proofs/LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108.json
{
  "tag": "LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108",
  "classification": "PASS_R5_NO_EXISTING_FILL_RUN_FOUND_ROUTE_TO_PATCH_IMPACT_OR_FUTURE_VALID_TRADE_DATASET",
  "patch_applied": false,
  "replay_executed": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "report": "run/audits/LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108_report.md"
}

## Git/source status
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
?? docs/milestones/LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108.md
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
?? docs/runbooks/LANE-B-R1_REPLAY_SURFACE_BASELINE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_120747_runbook.md
?? docs/runbooks/LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114_runbook.md
?? docs/runbooks/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738_runbook.md
?? docs/runbooks/LANE-B-R2D_R2C_REPLAY_ARTIFACT_SHAPE_COUNT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140338_runbook.md

## Current patch-impact clue scan in source
app/mme_scalpx/services/features.py:19:  MIST, MISB, MISC, MISR, MISO
app/mme_scalpx/services/features.py:167:FAMILY_MISB: Final[str] = getattr(N, "STRATEGY_FAMILY_MISB", "MISB")
app/mme_scalpx/services/features.py:176:        (FAMILY_MIST, FAMILY_MISB, FAMILY_MISC, FAMILY_MISR, FAMILY_MISO),
app/mme_scalpx/services/features.py:321:    FAMILY_MISB: "app.mme_scalpx.services.feature_family.misb_surface",
app/mme_scalpx/services/features.py:1538:        Additive only: this producer does not force tradability, candidates,
app/mme_scalpx/services/features.py:2477:                "provider_ready": classic != RUNTIME_DISABLED,
app/mme_scalpx/services/features.py:2482:                "provider_ready": miso != RUNTIME_DISABLED,
app/mme_scalpx/services/features.py:2647:        surface.setdefault("provider_ready", mode != RUNTIME_DISABLED)
app/mme_scalpx/services/features.py:2758:    def _family_provider_ready(
app/mme_scalpx/services/features.py:2769:        runtime_ready = bool(runtime_surface.get("provider_ready"))
app/mme_scalpx/services/features.py:2832:        provider_ready = self._family_provider_ready(
app/mme_scalpx/services/features.py:2848:            "provider_ready": provider_ready,
app/mme_scalpx/services/features.py:3187:            "provider_ready_classic": classic_mode != RUNTIME_DISABLED,
app/mme_scalpx/services/features.py:3188:            "provider_ready_miso": _batch26c_miso_provider_ready(
app/mme_scalpx/services/features.py:3460:                "provider_ready_classic": bool(provider.get("classic_runtime_mode") != RUNTIME_DISABLED),
app/mme_scalpx/services/features.py:3461:                "provider_ready_miso": _batch26c_miso_provider_ready(
app/mme_scalpx/services/features.py:3497:                "provider_ready": bool(provider.get("classic_runtime_mode") != RUNTIME_DISABLED),
app/mme_scalpx/services/features.py:3632:                    FAMILY_MISB: "build_empty_misb_branch_support",
app/mme_scalpx/services/features.py:3764:        if family_id == FAMILY_MISB:
app/mme_scalpx/services/features.py:3879:# No threshold changes. No candidate forcing. No paper/live/order enablement.
app/mme_scalpx/services/features.py:3982:        _b1_profit_live_r39we_score_bool(_b1_profit_live_r39we_pick(surface, "shelf_valid", "breakout_shelf_valid", default=False), 0.15),
app/mme_scalpx/services/features.py:4045:        "candidate_forced": False,
app/mme_scalpx/services/features.py:4200:    provider_ready_classic = _safe_bool(stage_flags.get("provider_ready_classic"), False)
app/mme_scalpx/services/features.py:4201:    provider_ready_miso = _safe_bool(stage_flags.get("provider_ready_miso"), False)
app/mme_scalpx/services/features.py:4228:        "provider_ready_classic": provider_ready_classic,
app/mme_scalpx/services/features.py:4229:        "provider_ready_miso": provider_ready_miso,
app/mme_scalpx/services/features.py:4244:            "miso_provider_ready_truth_preserved": provider_ready_miso,
app/mme_scalpx/services/features.py:4356:        # No signal, threshold, candidate, risk, execution, position, or order behavior is changed.
app/mme_scalpx/services/features.py:4798:    if "_batch25h_provider_ready_status" in globals():
app/mme_scalpx/services/features.py:4800:            return bool(_batch25h_provider_ready_status(value))  # type: ignore[name-defined]
app/mme_scalpx/services/features.py:4837:def _batch26c_miso_provider_ready(
app/mme_scalpx/services/features.py:4935:    # fail-closed below through provider_ready_miso and dhan_context_fresh.
app/mme_scalpx/services/features.py:4961:    provider_ready_classic = bool(
app/mme_scalpx/services/features.py:4973:    provider_ready_miso = _batch26c_miso_provider_ready(
app/mme_scalpx/services/features.py:4986:            and provider_ready_classic
app/mme_scalpx/services/features.py:4992:        out["data_valid"] and not snapshot_sync_valid and provider_ready_classic
app/mme_scalpx/services/features.py:4997:    out["provider_ready_classic"] = provider_ready_classic
app/mme_scalpx/services/features.py:4998:    out["provider_ready_miso"] = provider_ready_miso
app/mme_scalpx/services/features.py:5036:            if not flags.get("provider_ready_miso"):
app/mme_scalpx/services/features.py:5196:    active_ts_candidates = [ts for ts in (fut_ts, opt_ts) if ts is not None]
app/mme_scalpx/services/features.py:5197:    active_ts = max(active_ts_candidates) if active_ts_candidates else None
app/mme_scalpx/services/features.py:5201:    dhan_ts_candidates = [ts for ts in (dhan_fut_ts, dhan_opt_ts) if ts is not None]
app/mme_scalpx/services/features.py:5202:    dhan_ts = max(dhan_ts_candidates) if dhan_ts_candidates else None
app/mme_scalpx/services/features.py:5375:def _batch25h_provider_ready_status(status: Any) -> bool:
app/mme_scalpx/services/features.py:5444:        and _batch25h_provider_ready_status(out.get("futures_marketdata_status"))
app/mme_scalpx/services/features.py:5445:        and _batch25h_provider_ready_status(out.get("selected_option_marketdata_status"))
app/mme_scalpx/services/features.py:5453:        and _batch25h_provider_ready_status(out.get("futures_marketdata_status"))
app/mme_scalpx/services/features.py:5458:            and _batch25h_provider_ready_status(out.get("futures_marketdata_status"))
app/mme_scalpx/services/features.py:5464:        and _batch25h_provider_ready_status(out.get("selected_option_marketdata_status"))
app/mme_scalpx/services/features.py:5466:        and _batch25h_provider_ready_status(out.get("option_context_status"))
app/mme_scalpx/services/features.py:5469:    out["provider_ready_classic"] = classic_ready
app/mme_scalpx/services/features.py:5470:    out["provider_ready_miso"] = miso_ready
app/mme_scalpx/services/features.py:5582:    for candidate in keys:
app/mme_scalpx/services/features.py:5583:        value = source.get(candidate)
app/mme_scalpx/services/features.py:5705:    out["provider_ready_classic"] = classic_ready
app/mme_scalpx/services/features.py:5706:    out["provider_ready_miso"] = miso_ready
app/mme_scalpx/services/features.py:6138:            "provider_ready": bool(
app/mme_scalpx/services/features.py:6139:                surface.get("provider_ready")
app/mme_scalpx/services/features.py:6140:                if "provider_ready" in surface
app/mme_scalpx/services/features.py:6141:                else self._family_provider_ready(
app/mme_scalpx/services/features.py:6342:    candidate_keys: set[str] = set()
app/mme_scalpx/services/features.py:6345:            candidate_keys.add(canonical_key)
app/mme_scalpx/services/features.py:6346:            candidate_keys.update(str(alias) for alias in aliases)
app/mme_scalpx/services/features.py:6349:        candidate_keys.add(canonical_key)
app/mme_scalpx/services/features.py:6350:        candidate_keys.update(str(alias) for alias in aliases)
app/mme_scalpx/services/features.py:6356:        candidate_keys.discard("active_zone_valid")
app/mme_scalpx/services/features.py:6357:        candidate_keys.discard("zone_valid")
app/mme_scalpx/services/features.py:6358:        candidate_keys.discard("active_zone_ready")
app/mme_scalpx/services/features.py:6360:    return any(_safe_bool(rich_map.get(key), False) for key in candidate_keys if key in rich_map)
app/mme_scalpx/services/features.py:6499:                FAMILY_MISB: "build_empty_misb_branch_support",
app/mme_scalpx/services/features.py:6775:# - Does not mutate MISO readiness; preserves existing provider_ready_miso truth.
app/mme_scalpx/services/features.py:6979:        before_miso_ready = bool(flags.get("provider_ready_miso") is True)
app/mme_scalpx/services/features.py:6994:            flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:7007:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7012:        flags["provider_ready_miso"] = before_miso_ready
app/mme_scalpx/services/features.py:7019:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7113:                    "provider_ready_miso_before": before_miso_ready,
app/mme_scalpx/services/features.py:7114:                    "provider_ready_miso_after": bool(flags.get("provider_ready_miso") is True),
app/mme_scalpx/services/features.py:7135:# - No candidate forcing.
app/mme_scalpx/services/features.py:7177:    candidates = [
app/mme_scalpx/services/features.py:7187:        candidates.extend([
app/mme_scalpx/services/features.py:7195:            candidates.extend([
app/mme_scalpx/services/features.py:7204:    for c in candidates:
app/mme_scalpx/services/features.py:7261:        before_miso_ready = bool(flags.get("provider_ready_miso") is True)
app/mme_scalpx/services/features.py:7274:            flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:7288:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7292:        flags["provider_ready_miso"] = before_miso_ready
app/mme_scalpx/services/features.py:7299:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:7391:                    "forced_candidate": False,
app/mme_scalpx/services/features.py:7393:                    "provider_ready_miso_before": before_miso_ready,
app/mme_scalpx/services/features.py:7394:                    "provider_ready_miso_after": bool(flags.get("provider_ready_miso") is True),
app/mme_scalpx/services/features.py:7415:# - No candidate forcing.
app/mme_scalpx/services/features.py:7552:                "forced_candidate": False,
app/mme_scalpx/services/features.py:7574:# - No candidate forcing.
app/mme_scalpx/services/features.py:7747:                "forced_candidate": False,
app/mme_scalpx/services/features.py:7770:# - no candidate forcing
app/mme_scalpx/services/features.py:7915:                            "forced_candidate": False,
app/mme_scalpx/services/features.py:7941:# - no candidate forcing
app/mme_scalpx/services/features.py:7952:# - no candidate is forced.
app/mme_scalpx/services/features.py:7988:            if frame.get("family_id") not in {"MIST", "MISB", "MISC", "MISR", "MISO"}:
app/mme_scalpx/services/features.py:8007:            out["forced_candidate"] = False
app/mme_scalpx/services/features.py:8061:                            "forced_candidate": False,
app/mme_scalpx/services/features.py:8089:# - no candidate forcing
app/mme_scalpx/services/features.py:8106:# - no candidate is forced
app/mme_scalpx/services/features.py:8160:            if frame.get("family_id") not in {"MIST", "MISB", "MISC", "MISR", "MISO"}:
app/mme_scalpx/services/features.py:8176:            out["forced_candidate"] = False
app/mme_scalpx/services/features.py:8216:            "forced_candidate": False,
app/mme_scalpx/services/features.py:8254:# - no candidate forcing
app/mme_scalpx/services/features.py:8280:            if frame.get("family_id") not in {"MIST", "MISB", "MISC", "MISR", "MISO"}:
app/mme_scalpx/services/features.py:8300:        out["forced_candidate"] = False
app/mme_scalpx/services/features.py:8319:        "forced_candidate": False,
app/mme_scalpx/services/features.py:8336:# - no candidate forcing
app/mme_scalpx/services/features.py:8361:        out["forced_candidate"] = False
app/mme_scalpx/services/features.py:8381:        "forced_candidate": False,
app/mme_scalpx/services/features.py:8398:# - no candidate forcing
app/mme_scalpx/services/features.py:8434:                    cv2["forced_candidate"] = False
app/mme_scalpx/services/features.py:8663:        provider["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8667:        flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8673:            and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:8685:        provider["provider_ready_miso"] = False
app/mme_scalpx/services/features.py:8686:        flags["provider_ready_miso"] = False
app/mme_scalpx/services/features.py:8895:            provider["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8897:            flags["provider_ready_classic"] = True
app/mme_scalpx/services/features.py:8903:                and flags.get("provider_ready_classic")
app/mme_scalpx/services/features.py:8914:            provider["provider_ready_miso"] = False
app/mme_scalpx/services/features.py:8915:            flags["provider_ready_miso"] = False
app/mme_scalpx/services/features.py:8929:# - Add explicit micro-shelf fields for MISB/MISB-like breakout consumers.
app/mme_scalpx/services/features.py:8930:# - R5K/R5M4 proved MISB had provider_ready=true but failed shelf_validation
app/mme_scalpx/services/features.py:8931:#   because breakout_shelf_high/low/count were missing.
app/mme_scalpx/services/features.py:8935:# - No candidate forcing.
app/mme_scalpx/services/features.py:8981:        _b4_r5p_micro_pick(surface, "breakout_shelf_high", "shelf_high", "rolling_high", "lookback_high", "range_high") is not None
app/mme_scalpx/services/features.py:8982:        and _b4_r5p_micro_pick(surface, "breakout_shelf_low", "shelf_low", "rolling_low", "lookback_low", "range_low") is not None
app/mme_scalpx/services/features.py:9011:def _b4_r5p_apply_micro_shelf(self, surface):
app/mme_scalpx/services/features.py:9016:        out.setdefault("breakout_shelf_source", "upstream_explicit_shelf")
app/mme_scalpx/services/features.py:9021:        out.setdefault("breakout_shelf_source", "micro_shelf_no_valid_price")
app/mme_scalpx/services/features.py:9029:    history = getattr(self, "_b4_r5p_micro_shelf_history", None)
app/mme_scalpx/services/features.py:9032:        setattr(self, "_b4_r5p_micro_shelf_history", history)
app/mme_scalpx/services/features.py:9047:    out.setdefault("breakout_shelf_source", "micro_shelf")
app/mme_scalpx/services/features.py:9048:    out.setdefault("breakout_shelf_window_seconds", int(_B4_R5P_MICRO_SHELF_WINDOW_NS / 1_000_000_000))
app/mme_scalpx/services/features.py:9049:    out.setdefault("breakout_shelf_snapshot_count", count)
app/mme_scalpx/services/features.py:9055:        out.setdefault("breakout_shelf_missing_reason_hint", "micro_shelf_warming")
app/mme_scalpx/services/features.py:9065:    # Explicit MISB shelf fields.
app/mme_scalpx/services/features.py:9066:    out.setdefault("breakout_shelf_high", high)
app/mme_scalpx/services/features.py:9067:    out.setdefault("breakout_shelf_low", low)
app/mme_scalpx/services/features.py:9068:    out.setdefault("breakout_shelf_mid", mid)
app/mme_scalpx/services/features.py:9069:    out.setdefault("breakout_shelf_width", width)
app/mme_scalpx/services/features.py:9070:    out.setdefault("breakout_shelf_width_pct", width_pct)
app/mme_scalpx/services/features.py:9072:    # Compatibility aliases accepted by misb_surface._batch26e_breakout_shelf().
app/mme_scalpx/services/features.py:9093:def _b4_r5p_futures_surface_with_micro_shelf(
app/mme_scalpx/services/features.py:9106:    return _b4_r5p_apply_micro_shelf(self, surface)
app/mme_scalpx/services/features.py:9118:        "breakout_shelf_high",
app/mme_scalpx/services/features.py:9119:        "breakout_shelf_low",
app/mme_scalpx/services/features.py:9120:        "breakout_shelf_mid",
app/mme_scalpx/services/features.py:9121:        "breakout_shelf_width",
app/mme_scalpx/services/features.py:9122:        "breakout_shelf_width_pct",
app/mme_scalpx/services/features.py:9123:        "breakout_shelf_snapshot_count",
app/mme_scalpx/services/features.py:9124:        "breakout_shelf_source",
app/mme_scalpx/services/features.py:9125:        "breakout_shelf_window_seconds",
app/mme_scalpx/services/features.py:9153:FeatureEngine._futures_surface = _b4_r5p_futures_surface_with_micro_shelf
app/mme_scalpx/services/features.py:9162:# not force candidates, thresholds, MISO readiness, paper, execution, or orders.
app/mme_scalpx/services/features.py:9249:# - no forced candidate
app/mme_scalpx/services/features.py:9506:# LANE_X_R27E_MISB_PRIOR_SHELF_REF_BEGIN
app/mme_scalpx/services/features.py:9507:# Additive MISB prior-shelf breakout reference producer.
app/mme_scalpx/services/features.py:9509:# R27D proved the existing micro_shelf range is current-inclusive:
app/mme_scalpx/services/features.py:9510:# current LTP is appended before breakout_shelf_high/low are calculated.
app/mme_scalpx/services/features.py:9512:# extension when MISB compares current LTP against that same high/low.
app/mme_scalpx/services/features.py:9518:# - breakout_shelf_prior_high / breakout_shelf_prior_low
app/mme_scalpx/services/features.py:9522:# - no forced candidate
app/mme_scalpx/services/features.py:9652:                "breakout_shelf_prior_high": high,
app/mme_scalpx/services/features.py:9653:                "breakout_shelf_prior_low": low,
app/mme_scalpx/services/features.py:9654:                "breakout_shelf_prior_width": width,
app/mme_scalpx/services/features.py:9655:                "breakout_shelf_prior_width_pct": width_pct,
app/mme_scalpx/services/features.py:9656:                "breakout_shelf_prior_count": len(prices),
app/mme_scalpx/services/features.py:9657:                "breakout_shelf_ref_source": "prior_micro_shelf",
app/mme_scalpx/services/features.py:9685:        # separate prior-only reference keys for MISB breakout-extension logic.
app/mme_scalpx/services/features.py:9703:# LANE_X_R27E_MISB_PRIOR_SHELF_REF_END
app/mme_scalpx/services/features.py:9705:# LANE_X_R27G_MISB_PRIOR_REF_CONTRACT_PASSTHROUGH_BEGIN
app/mme_scalpx/services/features.py:9706:# Additive contract-block passthrough for R27E MISB prior shelf refs.
app/mme_scalpx/services/features.py:9713:# It does not change thresholds, does not force candidates, and does not weaken MISO.
app/mme_scalpx/services/features.py:9721:    "breakout_shelf_prior_high",
app/mme_scalpx/services/features.py:9722:    "breakout_shelf_prior_low",
app/mme_scalpx/services/features.py:9723:    "breakout_shelf_prior_width",
app/mme_scalpx/services/features.py:9724:    "breakout_shelf_prior_width_pct",
app/mme_scalpx/services/features.py:9725:    "breakout_shelf_prior_count",
app/mme_scalpx/services/features.py:9726:    "breakout_shelf_ref_source",
app/mme_scalpx/services/features.py:9749:# LANE_X_R27G_MISB_PRIOR_REF_CONTRACT_PASSTHROUGH_END
app/mme_scalpx/services/strategy.py:21:- MIST/MISB/MISC/MISR/MISO doctrine-leaf entry logic
app/mme_scalpx/services/strategy.py:413:    activation/report module observes candidates, this service may not publish
app/mme_scalpx/services/strategy.py:601:    provider_ready_classic: bool
app/mme_scalpx/services/strategy.py:602:    provider_ready_miso: bool
app/mme_scalpx/services/strategy.py:625:            "provider_ready_classic": self.provider_ready_classic,
app/mme_scalpx/services/strategy.py:626:            "provider_ready_miso": self.provider_ready_miso,
app/mme_scalpx/services/strategy.py:676:            allow_candidate_promotion=_r38r_controlled_paper_candidate_promotion_allowed(),
app/mme_scalpx/services/strategy.py:682:            min_candidate_score=0.0,
app/mme_scalpx/services/strategy.py:683:            max_candidates=10,
app/mme_scalpx/services/strategy.py:801:        provider_ready_classic = _safe_bool(stage_flags.get("provider_ready_classic"), False)
app/mme_scalpx/services/strategy.py:802:        provider_ready_miso = _safe_bool(stage_flags.get("provider_ready_miso"), False)
app/mme_scalpx/services/strategy.py:827:            provider_ready_classic=provider_ready_classic,
app/mme_scalpx/services/strategy.py:828:            provider_ready_miso=provider_ready_miso,
app/mme_scalpx/services/strategy.py:873:                "candidates": [],
app/mme_scalpx/services/strategy.py:895:            if _r38r_controlled_paper_candidate_promotion_allowed() and observed_safe_to_promote:
app/mme_scalpx/services/strategy.py:909:        # Diagnostic-only: does not change action, candidate selection, risk, execution, broker, order, replay, or PnL.
app/mme_scalpx/services/strategy.py:952:        activation_candidates = activation_report.get("candidates")
app/mme_scalpx/services/strategy.py:953:        activation_candidate_count = (
app/mme_scalpx/services/strategy.py:954:            len(activation_candidates)
app/mme_scalpx/services/strategy.py:955:            if isinstance(activation_candidates, list)
app/mme_scalpx/services/strategy.py:997:            "activation_candidate_count": activation_candidate_count,
app/mme_scalpx/services/strategy.py:1001:            "provider_ready_classic": int(view.provider_ready_classic),
app/mme_scalpx/services/strategy.py:1002:            "provider_ready_miso": int(view.provider_ready_miso),
app/mme_scalpx/services/strategy.py:1016:                    "activation_candidate_count": activation_candidate_count,
app/mme_scalpx/services/strategy.py:1087:        # Serialization-only. No strategy decision, candidate, threshold, risk, execution, position, or order behavior is changed.
app/mme_scalpx/services/strategy.py:1102:        # No strategy decision, candidate, threshold, risk, execution, position, broker, paper, or live behavior is changed.
app/mme_scalpx/services/strategy.py:1133:                            "is_candidate": _safe_bool(_item.get("is_candidate"), False),
app/mme_scalpx/services/strategy.py:1156:                    _o23q_r13_candidates = _o23q_r13_norm_list(
app/mme_scalpx/services/strategy.py:1157:                        _o23q_r13_activation_obj.get("candidates")
app/mme_scalpx/services/strategy.py:1167:                        "schema": "o23q_family_scope_candidates_v1",
app/mme_scalpx/services/strategy.py:1177:                        "candidates": _o23q_r13_candidates,
app/mme_scalpx/services/strategy.py:1180:                        "candidate_count": len(_o23q_r13_candidates),
app/mme_scalpx/services/strategy.py:1184:                    fields["family_scope_candidates_json"] = json.dumps(
app/mme_scalpx/services/strategy.py:1189:                    fields["o23q_r13_family_scope_candidates_projection_patch"] = "1"

## Lane X / R5P / MISB patch evidence files
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
docs/milestones/LANE-X-CLOSE-R3_corrected_pseal_completion_finalizer_20260604_152311.md
docs/milestones/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203209.md
docs/milestones/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203215.md
docs/milestones/LANE-X-DASH-R1_dashboard_lane_evidence_bundle_no_patch_no_order_20260604_230829.md
docs/milestones/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059.md
docs/milestones/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421.md
docs/milestones/LANE-X-DASH-R2B-TINY-SEAL_STATIC_OBSERVE_PANEL_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_seal_existing_lx_tiny_source_markers_compile_import_ast_safety_20260604_232058.md
docs/milestones/LANE-X-DASH-R2C_RUNTIME_SEAL_LX_TINY_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER_restart_dashboard_only_and_seal_running_lane_x_observe_page_markers_20260604_232202.md
docs/milestones/LANE-X-PDISK-R1_safe_cleanup_inventory_no_delete_20260604_210232.md
docs/milestones/LANE-X-PDISK-R2_explicit_cleanup_plan_no_delete_20260604_210418.md
docs/milestones/LANE-X-R12_day4_evidence_index_no_patch_no_order_20260604_203314.md
docs/milestones/LANE-X-R13B_sealed_data_integrity_finalizer_exclude_self_sha_20260604_203618.md
docs/milestones/LANE-X-R13_sealed_data_integrity_audit_no_patch_no_replay_no_order_20260604_203422.md
docs/milestones/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712.md
docs/milestones/LANE-X-R15_misb_shelf_width_distribution_audit_no_patch_no_replay_no_order_20260604_203827.md
docs/milestones/LANE-X-R16_mist_response_futures_impulse_audit_no_patch_no_replay_no_order_20260604_204031.md
docs/milestones/LANE-X-R17B_compact_snapshot_sync_view_data_invalid_finalizer_20260604_205244.md
docs/milestones/LANE-X-R17_snapshot_sync_view_data_invalid_audit_no_patch_no_replay_no_order_20260604_204256.md
docs/milestones/LANE-X-R18_dhan_miso_unavailable_audit_no_patch_no_replay_no_order_20260604_205403.md
docs/milestones/LANE-X-R19A_helper_source_locator_no_patch_no_order_20260604_205537.md
docs/milestones/LANE-X-R19B_pcheck_disk_emoji_helper_patch_no_order_20260604_205659.md
docs/milestones/LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815.md
docs/milestones/LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936.md
docs/milestones/LANE-X-R20_day4_consolidated_milestone_and_tomorrow_plan_no_patch_no_order_20260604_210132.md
docs/milestones/LANE-X-R21_family_strategy_source_review_bundle_no_patch_no_order_20260604_211329.md
docs/milestones/LANE-X-R22A_mist_micro_option_response_source_seam_audit_no_patch_no_order_20260604_211933.md
docs/milestones/LANE-X-R22B-DIAG_micro_option_response_context_no_patch_no_order_20260604_224928.md
docs/milestones/LANE-X-R22B-REPAIR_micro_option_response_return_path_repair_no_start_no_order_20260604_225050.md
docs/milestones/LANE-X-R22B_micro_option_response_producer_patch_no_start_no_order_20260604_224759.md
docs/milestones/LANE-X-R22C-R2_corrected_mist_branch_consumer_micro_response_selftest_no_start_no_order_20260604_225319.md
docs/milestones/LANE-X-R22C_mist_consumer_micro_response_selftest_no_start_no_order_20260604_225141.md
docs/milestones/LANE-X-R22D_micro_option_response_patch_finalizer_tomorrow_live_validation_no_start_no_order_20260604_225437.md
docs/milestones/LANE-X-R23_post_r22_micro_response_evidence_bundle_no_patch_no_order_20260604_225905.md
docs/milestones/LANE-X-R24A_opportunity_expansion_source_seam_audit_no_patch_no_order_20260604_230020.md
docs/milestones/LANE-X-R24B_shadow_near_candidate_observer_helper_no_production_candidate_no_order_20260604_230313.md
docs/milestones/LANE-X-R24C_post_r24b_shadow_near_candidate_finalizer_no_patch_no_order_20260604_230456.md
docs/milestones/LANE-X-R25A_friday_premarket_r22_r24b_readiness_no_start_no_order_20260605_091006.md
docs/milestones/LANE-X-R25A_friday_premarket_r22_r24b_readiness_no_start_no_order_20260605_091015.md
docs/milestones/LANE-X-R25B-WAIT_post_open_health_recheck_no_start_no_stop_no_order_20260605_091425.md
docs/milestones/LANE-X-R25B-WAIT_post_open_health_recheck_no_start_no_stop_no_order_20260605_091611.md
docs/milestones/LANE-X-R25B_friday_observe_only_start_or_reuse_no_patch_no_order_20260605_091243.md
docs/milestones/LANE-X-R25C_features_strategy_stale_log_triage_no_start_no_stop_no_patch_no_order_20260605_091725.md
docs/milestones/LANE-X-R25D_r22b_wrapper_side_kwarg_hotfix_no_start_no_stop_no_order_20260605_091906.md
docs/milestones/LANE-X-R25E_refresh_features_strategy_after_r25d_hotfix_no_feeds_no_order_20260605_092014.md
docs/milestones/LANE-X-R25F_recover_missing_features_strategy_after_r25e_no_kill_no_feeds_no_order_20260605_092129.md
docs/milestones/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342.md
docs/milestones/LANE-X-R25H_feature_consumer_view_provider_ready_inspector_no_patch_no_order_20260605_092458.md
docs/milestones/LANE-X-R25J_rolling_r22_snapshot_tradability_sampler_no_patch_no_order_20260605_093000.md
docs/milestones/LANE-X-R25K_futures_source_inventory_after_fut_missing_pcheck_no_patch_no_order_20260605_095301.md
docs/milestones/LANE-X-R25L_option_side_role_consistency_sampler_no_patch_no_order_20260605_095512.md
docs/milestones/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_104251.md
docs/milestones/LANE-X-R25M_invalid_member_anomaly_clamped_sampler_no_patch_no_order_20260605_101117.md
docs/milestones/LANE-X-R25N_shadow_opportunity_snapshot_freeze_no_patch_no_order_20260605_134052.md
docs/milestones/LANE-X-R25N_valid_frame_family_opportunity_sampler_no_patch_no_order_20260605_110051.md
docs/milestones/LANE-X-R25O_candidate_promotion_gap_inspector_no_patch_no_order_20260605_110846.md
docs/milestones/LANE-X-R25O_day5_pseal_completion_finalizer_no_patch_no_order_20260605_152150.md
docs/milestones/LANE-X-R25P_day5_compact_evidence_bundle_no_patch_no_order_20260605_152449.md
docs/milestones/LANE-X-R25P_mist_futures_impulse_gap_inspector_no_patch_no_order_20260605_111037.md
docs/milestones/LANE-X-R25R_futures_kinetic_primitive_gap_sampler_no_patch_no_order_20260605_112133.md
docs/milestones/LANE-X-R25T_readonly_hypothetical_futures_kinetics_from_raw_ticks_no_patch_no_order_20260605_113952.md
docs/milestones/LANE-X-R26A_day5_bundle_root_cause_freeze_no_patch_no_order_20260607_112913.md
docs/milestones/LANE-X-R26B_micro_futures_kinetics_producer_patch_no_start_no_order_20260607_113211.md
docs/milestones/LANE-X-R26C_micro_futures_kinetics_mist_consumer_selftest_no_patch_no_order_20260607_113339.md
docs/milestones/LANE-X-R26D-R2_corrected_redisraw_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113823.md
docs/milestones/LANE-X-R26D-R3_preserve_blank_values_redisraw_futures_kinetics_validator_no_patch_no_order_20260607_114851.md
docs/milestones/LANE-X-R26D-R4_chronological_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_115028.md
docs/milestones/LANE-X-R26D_day5_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113438.md
docs/milestones/LANE-X-R26E_micro_futures_kinetics_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_115137.md
docs/milestones/LANE-X-R26F_micro_futures_kinetics_chain_evidence_bundle_no_patch_no_order_20260607_115245.md
docs/milestones/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657.md
docs/milestones/LANE-X-R27B_misb_shelf_width_scale_window_audit_no_patch_no_order_20260607_115937.md
docs/milestones/LANE-X-R27C_misb_shelf_threshold_scenario_quality_audit_no_patch_no_order_20260607_120106.md
docs/milestones/LANE-X-R27D_misb_current_inclusive_shelf_reference_audit_no_patch_no_order_20260607_120243.md
docs/milestones/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500.md
docs/milestones/LANE-X-R27F_sealed_prior_shelf_ref_contract_passthrough_validator_no_patch_no_order_20260607_120622.md
docs/milestones/LANE-X-R27G_misb_prior_shelf_ref_contract_passthrough_patch_no_start_no_order_20260607_120850.md
docs/milestones/LANE-X-R27H_rerun_sealed_prior_ref_contract_passthrough_validator_no_patch_no_order_20260607_121008.md
docs/milestones/LANE-X-R27I_misb_prior_shelf_ref_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_121138.md
docs/milestones/LANE-X-R27J_misb_prior_shelf_ref_chain_evidence_bundle_no_patch_no_order_20260607_121241.md
docs/milestones/LANE-X-R28A_weekend_consolidated_finalizer_monday_observe_checklist_no_patch_no_order_20260607_121432.md
docs/milestones/LANE-X-R28B_final_weekend_observe_ready_evidence_bundle_no_patch_no_order_20260607_121600.md
docs/milestones/LANE-X-R29A-R4_PREMARKET_RECONNECT_MINI_AUDIT_NO_PATCH_NO_START_NO_ORDER_after_ssh_drop_verify_no_side_effect_source_safety_r28b_ready_20260607_135037.md
docs/milestones/LANE-X-R29B-R1_INTERRUPTED_SUNDAY_START_ATTEMPT_SIDE_EFFECT_AUDIT_NO_PATCH_NO_START_NO_ORDER_verify_r29b_interrupted_paste_did_not_start_risk_execution_or_order_20260607_135857.md
docs/milestones/LANE-X-R29B-R2_MINIMAL_MONDAY_OBSERVE_ONLY_START_REUSE_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_minimal_helper_based_start_reuse_after_r29a_pass_20260607_135950.md
docs/milestones/LANE-X-R30A_FAMILY_MICROSTRUCTURE_COVERAGE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_mist_misb_misc_misr_miso_required_microstructure_surfaces_and_contract_passthrough_20260607_140857.md
docs/milestones/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044.md
docs/milestones/LANE-X-R30D_PROVIDER_RUNTIME_KEY_CONTRACT_ALIGNMENT_AUDIT_NO_PATCH_NO_START_NO_ORDER_compare_names_provider_runtime_publishers_readers_pcheck_expected_redis_keys_20260607_141254.md
docs/runbooks/B4-DAY3-R5D_MISB_SCORE_FORMULA_REPRODUCER_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_misb_evaluate_score_parts_formula_min_score_gate_and_reproduce_0359938_from_a7_nearest_20260603_224756_runbook.md
docs/runbooks/B4-DAY3-R5E_MISB_COMPUTE_SCORE_EXACT_FORMULA_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_full_compute_score_body_component_weights_min_score_gate_and_activation_vs_alias_surface_input_lineage_20260603_224931_runbook.md
docs/runbooks/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225603_runbook.md
docs/runbooks/B4-DAY3-R5F_MISB_BREAKOUT_SCORE_INPUT_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_extract_actual_misb_call_surface_breakout_fields_that_feed_compute_score_0004615_20260603_225709_runbook.md
docs/runbooks/B4-DAY3-R5G_MISB_PROVIDER_NOT_READY_SURFACE_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_trace_failed_stage_provider_not_ready_from_features_surface_to_misb_evaluate_without_runtime_mutation_20260603_230017_runbook.md
docs/runbooks/B4-DAY3-R5J_MISB_SHELF_VALIDATION_LINEAGE_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231305_runbook.md
docs/runbooks/B4-DAY3-R5K_MISB_SHELF_MISSING_REASON_READONLY_NO_PATCH_NO_START_NO_ORDER_20260603_231945_runbook.md
docs/runbooks/B4-DAY3-R5_READ_ONLY_MISB_CALL_SCORE_DECOMPOSITION_AUDIT_NO_PATCH_NO_START_NO_ORDER_extract_exact_misb_call_score_path_nearest_miss_threshold_regime_breakout_and_activation_candidate_chain_20260603_223351_runbook.md
docs/runbooks/BATCH30J_R5P_REAL_INTEGRITY_CHECK_IMPLEMENTATION_PLAN_RUNBOOK.md
docs/runbooks/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_runbook.md
docs/runbooks/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421_runbook.md
docs/runbooks/LANE-X-DASH-R2B-TINY-SEAL_STATIC_OBSERVE_PANEL_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_seal_existing_lx_tiny_source_markers_compile_import_ast_safety_20260604_232058_runbook.md
docs/runbooks/LANE-X-DASH-R2C_RUNTIME_SEAL_LX_TINY_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER_restart_dashboard_only_and_seal_running_lane_x_observe_page_markers_20260604_232202_runbook.md
docs/runbooks/LANE-X-R28A_weekend_consolidated_finalizer_monday_observe_checklist_no_patch_no_order_20260607_121432_monday_observe_only_runbook.md
docs/runbooks/LANE-X-R29A-R4_PREMARKET_RECONNECT_MINI_AUDIT_NO_PATCH_NO_START_NO_ORDER_after_ssh_drop_verify_no_side_effect_source_safety_r28b_ready_20260607_135037_runbook.md
docs/runbooks/LANE-X-R30A_FAMILY_MICROSTRUCTURE_COVERAGE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_mist_misb_misc_misr_miso_required_microstructure_surfaces_and_contract_passthrough_20260607_140857_runbook.md
docs/runbooks/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_runbook.md
docs/runbooks/LANE-X-R30D_PROVIDER_RUNTIME_KEY_CONTRACT_ALIGNMENT_AUDIT_NO_PATCH_NO_START_NO_ORDER_compare_names_provider_runtime_publishers_readers_pcheck_expected_redis_keys_20260607_141254_runbook.md
run/_code_backups/B4-R5P_MICRO_SHELF_PRODUCER_PATCH_NO_START_NO_ORDER_20260603_234829_features.py.bak
run/_code_backups/LANE-X-DASH-R2B-TINY_STATIC_OBSERVE_PANEL_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER_20260604_232007_server.py.bak
run/_code_backups/LANE-X-R19B_pcheck_disk_emoji_helper_patch_no_order_20260604_205659_bash_aliases.backup
run/_code_backups/LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936_bashrc.backup
run/_code_backups/LANE-X-R22B-REPAIR_micro_option_response_return_path_repair_no_start_no_order_20260604_225050_features.py.backup
run/_code_backups/LANE-X-R22B_micro_option_response_producer_patch_no_start_no_order_20260604_224759_features.py.backup
run/_code_backups/LANE-X-R25D_r22b_wrapper_side_kwarg_hotfix_no_start_no_stop_no_order_20260605_091906_features.py.backup
run/_code_backups/LANE-X-R26B_micro_futures_kinetics_producer_patch_no_start_no_order_20260607_113211_features.py.backup
run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_features.py.backup
run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_misb_surface.py.backup
run/_code_backups/LANE-X-R27G_misb_prior_shelf_ref_contract_passthrough_patch_no_start_no_order_20260607_120850_features.py.backup
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
run/audits/LANE-X-CLOSE-R1_safe_pseal_close_freeze_20260604_151928_raw.txt
run/audits/LANE-X-CLOSE-R2_verify_pseal_completion_20260604_152157_raw.txt
run/audits/LANE-X-CLOSE-R3_corrected_pseal_completion_finalizer_20260604_152311_raw.txt
run/audits/LANE-X-CLOSE-R4_final_post_r11_pseal_freeze_20260604_203022_raw.txt
run/audits/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203209_raw.txt
run/audits/LANE-X-CLOSE-R5_verify_r4_post_r11_pseal_completion_20260604_203215_raw.txt
run/audits/LANE-X-DASH-R1_dashboard_lane_evidence_bundle_no_patch_no_order_20260604_230829_filelist.txt
run/audits/LANE-X-DASH-R1_dashboard_lane_evidence_bundle_no_patch_no_order_20260604_230829_raw.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_dashboard_source_audit.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_lane_x_proof_chain.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_report.md
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_safety_state.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_shadow_near_candidate_output.txt
run/audits/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421_report.md
run/audits/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421_source_audit.txt
run/audits/LANE-X-DASH-R2B-TINY-SEAL_STATIC_OBSERVE_PANEL_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_seal_existing_lx_tiny_source_markers_compile_import_ast_safety_20260604_232058_extract.txt
run/audits/LANE-X-DASH-R2B-TINY-SEAL_STATIC_OBSERVE_PANEL_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_seal_existing_lx_tiny_source_markers_compile_import_ast_safety_20260604_232058_report.md
run/audits/LANE-X-DASH-R2C_RUNTIME_SEAL_LX_TINY_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER_restart_dashboard_only_and_seal_running_lane_x_observe_page_markers_20260604_232202_page_markers.txt
run/audits/LANE-X-DASH-R2C_RUNTIME_SEAL_LX_TINY_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER_restart_dashboard_only_and_seal_running_lane_x_observe_page_markers_20260604_232202_page_snapshot.html
run/audits/LANE-X-DASH-R2C_RUNTIME_SEAL_LX_TINY_DASHBOARD_ONLY_NO_START_NO_ORDER_NO_PAPER_restart_dashboard_only_and_seal_running_lane_x_observe_page_markers_20260604_232202_report.md
run/audits/LANE-X-PDISK-R1_safe_cleanup_inventory_no_delete_20260604_210232_raw.txt
run/audits/LANE-X-PDISK-R1_safe_cleanup_inventory_no_delete_20260604_210232_report.md
run/audits/LANE-X-PDISK-R2_explicit_cleanup_plan_no_delete_20260604_210418_cleanup_plan.md
run/audits/LANE-X-PDISK-R2_explicit_cleanup_plan_no_delete_20260604_210418_raw.txt
run/audits/LANE-X-R0B_helper_discovery_20260604_093205_raw.txt
run/audits/LANE-X-R0_prestart_verify_20260604_093055_raw.txt
run/audits/LANE-X-R10_rolling_nearest_miss_sampler_20260604_100336_raw.txt
run/audits/LANE-X-R10_rolling_nearest_miss_sampler_20260604_100336_samples.csv
run/audits/LANE-X-R11_final_live_close_window_sampler_20260604_152512_raw.txt
run/audits/LANE-X-R11_final_live_close_window_sampler_20260604_152512_samples.csv
run/audits/LANE-X-R12_day4_evidence_index_no_patch_no_order_20260604_203314_raw.txt
run/audits/LANE-X-R13B_sealed_data_integrity_finalizer_exclude_self_sha_20260604_203618_R4_SHA256SUMS_excluding_self.txt
run/audits/LANE-X-R13B_sealed_data_integrity_finalizer_exclude_self_sha_20260604_203618_raw.txt
run/audits/LANE-X-R13_sealed_data_integrity_audit_no_patch_no_replay_no_order_20260604_203422_raw.txt
run/audits/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712_raw.txt
run/audits/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712_report.md
run/audits/LANE-X-R15_misb_shelf_width_distribution_audit_no_patch_no_replay_no_order_20260604_203827_raw.txt
run/audits/LANE-X-R15_misb_shelf_width_distribution_audit_no_patch_no_replay_no_order_20260604_203827_report.md
run/audits/LANE-X-R16_mist_response_futures_impulse_audit_no_patch_no_replay_no_order_20260604_204031_raw.txt
run/audits/LANE-X-R16_mist_response_futures_impulse_audit_no_patch_no_replay_no_order_20260604_204031_report.md
run/audits/LANE-X-R17B_compact_snapshot_sync_view_data_invalid_finalizer_20260604_205244_raw.txt
run/audits/LANE-X-R17B_compact_snapshot_sync_view_data_invalid_finalizer_20260604_205244_report.md
run/audits/LANE-X-R17_snapshot_sync_view_data_invalid_audit_no_patch_no_replay_no_order_20260604_204256_raw.txt
run/audits/LANE-X-R17_snapshot_sync_view_data_invalid_audit_no_patch_no_replay_no_order_20260604_204256_report.md
run/audits/LANE-X-R18_dhan_miso_unavailable_audit_no_patch_no_replay_no_order_20260604_205403_raw.txt
run/audits/LANE-X-R18_dhan_miso_unavailable_audit_no_patch_no_replay_no_order_20260604_205403_report.md
run/audits/LANE-X-R19A_helper_source_locator_no_patch_no_order_20260604_205537_raw.txt
run/audits/LANE-X-R19A_helper_source_locator_no_patch_no_order_20260604_205537_report.md
run/audits/LANE-X-R19B_pcheck_disk_emoji_helper_patch_no_order_20260604_205659_raw.txt
run/audits/LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815_raw.txt
run/audits/LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815_report.md
run/audits/LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936_raw.txt
run/audits/LANE-X-R1_live_observe_only_start_20260604_093504_raw.txt
run/audits/LANE-X-R20_day4_consolidated_milestone_and_tomorrow_plan_no_patch_no_order_20260604_210132_raw.txt
run/audits/LANE-X-R21_family_strategy_source_review_bundle_no_patch_no_order_20260604_211329_filelist.txt
run/audits/LANE-X-R21_family_strategy_source_review_bundle_no_patch_no_order_20260604_211329_raw.txt
run/audits/LANE-X-R22A_mist_micro_option_response_source_seam_audit_no_patch_no_order_20260604_211933_raw.txt
run/audits/LANE-X-R22A_mist_micro_option_response_source_seam_audit_no_patch_no_order_20260604_211933_report.md
run/audits/LANE-X-R22B-DIAG_micro_option_response_context_no_patch_no_order_20260604_224928_raw.txt
run/audits/LANE-X-R22B-DIAG_micro_option_response_context_no_patch_no_order_20260604_224928_report.md
run/audits/LANE-X-R22B-REPAIR_micro_option_response_return_path_repair_no_start_no_order_20260604_225050_raw.txt
run/audits/LANE-X-R22B_micro_option_response_producer_patch_no_start_no_order_20260604_224759_raw.txt
run/audits/LANE-X-R22C-R2_corrected_mist_branch_consumer_micro_response_selftest_no_start_no_order_20260604_225319_raw.txt
run/audits/LANE-X-R22C_mist_consumer_micro_response_selftest_no_start_no_order_20260604_225141_raw.txt
run/audits/LANE-X-R22D_micro_option_response_patch_finalizer_tomorrow_live_validation_no_start_no_order_20260604_225437_raw.txt
run/audits/LANE-X-R23_post_r22_micro_response_evidence_bundle_no_patch_no_order_20260604_225905_filelist.txt
run/audits/LANE-X-R23_post_r22_micro_response_evidence_bundle_no_patch_no_order_20260604_225905_raw.txt
run/audits/LANE-X-R24A_opportunity_expansion_source_seam_audit_no_patch_no_order_20260604_230020_raw.txt
run/audits/LANE-X-R24A_opportunity_expansion_source_seam_audit_no_patch_no_order_20260604_230020_report.md
run/audits/LANE-X-R24B_shadow_near_candidate_observer_helper_no_production_candidate_no_order_20260604_230313_raw.txt
run/audits/LANE-X-R24B_shadow_near_candidate_observer_helper_no_production_candidate_no_order_20260604_230313_shadow_near_candidate_summary.json
run/audits/LANE-X-R24C_post_r24b_shadow_near_candidate_finalizer_no_patch_no_order_20260604_230456_raw.txt
run/audits/LANE-X-R25A_friday_premarket_r22_r24b_readiness_no_start_no_order_20260605_091006_raw.txt
run/audits/LANE-X-R25A_friday_premarket_r22_r24b_readiness_no_start_no_order_20260605_091015_raw.txt
run/audits/LANE-X-R25B-WAIT_post_open_health_recheck_no_start_no_stop_no_order_20260605_091425_raw.txt
run/audits/LANE-X-R25B-WAIT_post_open_health_recheck_no_start_no_stop_no_order_20260605_091611_raw.txt
run/audits/LANE-X-R25B_friday_observe_only_start_or_reuse_no_patch_no_order_20260605_091243_raw.txt
run/audits/LANE-X-R25C_features_strategy_stale_log_triage_no_start_no_stop_no_patch_no_order_20260605_091725_raw.txt
run/audits/LANE-X-R25D_r22b_wrapper_side_kwarg_hotfix_no_start_no_stop_no_order_20260605_091906_raw.txt
run/audits/LANE-X-R25E_refresh_features_strategy_after_r25d_hotfix_no_feeds_no_order_20260605_092014_raw.txt
run/audits/LANE-X-R25F_recover_missing_features_strategy_after_r25e_no_kill_no_feeds_no_order_20260605_092129_raw.txt
run/audits/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342_raw.txt
run/audits/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342_report.txt
run/audits/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342_shadow_near_candidate.json
run/audits/LANE-X-R25H_feature_consumer_view_provider_ready_inspector_no_patch_no_order_20260605_092458_raw.txt
run/audits/LANE-X-R25H_feature_consumer_view_provider_ready_inspector_no_patch_no_order_20260605_092458_report.txt
run/audits/LANE-X-R25J_rolling_r22_snapshot_tradability_sampler_no_patch_no_order_20260605_093000_raw.txt
run/audits/LANE-X-R25J_rolling_r22_snapshot_tradability_sampler_no_patch_no_order_20260605_093000_samples.csv
run/audits/LANE-X-R25K_futures_source_inventory_after_fut_missing_pcheck_no_patch_no_order_20260605_095301_raw.txt
run/audits/LANE-X-R25L_option_side_role_consistency_sampler_no_patch_no_order_20260605_095512_raw.txt
run/audits/LANE-X-R25L_option_side_role_consistency_sampler_no_patch_no_order_20260605_095512_samples.csv
run/audits/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_104251_raw.txt
run/audits/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_104251_samples.csv
run/audits/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_105944_raw.txt

## Candidate baseline backup/source snapshots
run/_code_backups/B1-PROFIT-LIVE-R38ZR_STRATEGY_FEATURE_CONTRACT_COMPAT_PATCH_NO_START_NO_STOP_NO_ORDER_minimal_report_only_consumer_bridge_provider_runtime_backfill_for_feature_family_contract_error_20260601_093056/strategy.py.bak
run/_code_backups/B4-DAY3-R4B_R39WM_DYNAMIC_SCORE_DERIVATION_PATCH_RETRY_NO_START_NO_ORDER_retry_guarded_features_dynamic_score_derivation_fix_callsite_counter_compile_import_selftest_20260603_222810_features.py.bak
run/_code_backups/B4-DAY3-R4C_R39WM_R2_COMPILE_FAIL_ROLLBACK_NO_START_NO_ORDER_restore_features_py_from_pre_r39wm_r2_backup_after_indentation_error_20260603_222947_failed_features.py
run/_code_backups/B4-DAY3-R4_R39WM_DYNAMIC_SCORE_DERIVATION_PATCH_NO_START_NO_ORDER_apply_guarded_features_dynamic_score_derivation_before_r39we_valid_local_sites_compile_import_selftest_20260603_222607_features.py.bak
run/_code_backups/B4-R5P_MICRO_SHELF_PRODUCER_PATCH_NO_START_NO_ORDER_20260603_234829_features.py.bak
run/_code_backups/LANE-X-DASH-R2B-TINY_STATIC_OBSERVE_PANEL_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER_20260604_232007_server.py.bak
run/_code_backups/LANE-X-R19B_pcheck_disk_emoji_helper_patch_no_order_20260604_205659_bash_aliases.backup
run/_code_backups/LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936_bashrc.backup
run/_code_backups/LANE-X-R22B-REPAIR_micro_option_response_return_path_repair_no_start_no_order_20260604_225050_features.py.backup
run/_code_backups/LANE-X-R22B_micro_option_response_producer_patch_no_start_no_order_20260604_224759_features.py.backup
run/_code_backups/LANE-X-R25D_r22b_wrapper_side_kwarg_hotfix_no_start_no_stop_no_order_20260605_091906_features.py.backup
run/_code_backups/LANE-X-R26B_micro_futures_kinetics_producer_patch_no_start_no_order_20260607_113211_features.py.backup
run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_features.py.backup
run/_code_backups/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_misb_surface.py.backup
run/_code_backups/LANE-X-R27G_misb_prior_shelf_ref_contract_passthrough_patch_no_start_no_order_20260607_120850_features.py.backup
run/audits/A6-FEED-R4B_canonical_provider_feed_hash_publication_diagnostic_no_patch_no_order_no_broker_20260512_132348.txt
run/audits/A6-FEED-R4R_post_r4q_feed_health_regression_and_provider_mapping_diagnostic_no_patch_no_write_no_order_no_broker_20260512_152600.txt
run/audits/A6-FEED-R5-D_feature_decision_provider_blocker_source_mapping_no_patch_no_order_20260512_142230_audit.json
run/audits/A6-FEED-R5-J_source_patch_minimal_durable_canonical_provider_feed_hash_owner_no_paper_no_live_no_broker_order_20260512_150847_audit.json
run/audits/A6-FEED-R5B2-AM_after_market_saved_artifact_provider_mapping_classifier_no_live_no_patch_no_write_no_order_no_broker_20260513_073016.json
run/audits/A6-FEED-R5B_feature_provider_ready_mapping_classifier_no_patch_no_write_no_order_no_broker_20260512_152846.txt
run/audits/A6-FEED-R5C_provider_surface_degraded_unsynced_feature_mapping_patch_plan_no_patch_no_write_no_order_no_broker_20260513_073404.txt
run/audits/A6-FEED-R5D_approved_minimal_features_provider_mapping_patch_no_order_no_broker_no_threshold_change_20260513_073613.txt
run/audits/A6-FEED-R5E_features_provider_mapping_patch_static_compile_contract_proof_no_start_no_order_no_broker_20260513_073738.txt
run/audits/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011.txt
run/audits/A6-LIVE-R2I-D2_compact_proof_recovery_and_provider_not_ready_classifier_no_source_patch_no_order_no_broker_audit_20260512_102846.json
run/audits/A6-LIVE-R2I-E_provider_feed_surface_recovery_diagnostic_no_source_patch_no_order_no_broker_audit_20260512_103359.json
run/audits/A6-LIVE-R2I-G_feed_provider_error_classifier_no_source_patch_no_order_no_broker_audit_20260512_103858.json
run/audits/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701_audit.json
run/audits/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701_status_report.md
run/audits/B1-PROFIT-LIVE-R0_CLASSIC_CANDIDATE_AND_DHAN_CONTEXT_GROWTH_AUDIT_NO_ORDER_live_session_audit_pfeeds_pstack_dhan_context_classic_candidate_growth_no_patch_no_start_no_order_20260521_094211_audit.json
run/audits/B1-PROFIT-LIVE-R0_CLASSIC_CANDIDATE_AND_DHAN_CONTEXT_GROWTH_AUDIT_NO_ORDER_live_session_audit_pfeeds_pstack_dhan_context_classic_candidate_growth_no_patch_no_start_no_order_20260521_094211_live_growth_candidate_report.md
run/audits/B1-PROFIT-LIVE-R13_POST_R12_SINGLE_STRATEGY_ENV_AND_LOCK_OWNER_AUDIT_NO_ORDER_read_only_audit_remaining_strategy_env_lock_owner_and_candidate_signal_after_r12_no_patch_no_start_no_stop_no_kill_no_delete_no_order_20260521_124333_audit.json
run/audits/B1-PROFIT-LIVE-R13_POST_R12_SINGLE_STRATEGY_ENV_AND_LOCK_OWNER_AUDIT_NO_ORDER_read_only_audit_remaining_strategy_env_lock_owner_and_candidate_signal_after_r12_no_patch_no_start_no_stop_no_kill_no_delete_no_order_20260521_125352_audit.json
run/audits/B1-PROFIT-LIVE-R13_POST_R12_SINGLE_STRATEGY_ENV_AND_LOCK_OWNER_AUDIT_NO_ORDER_read_only_audit_remaining_strategy_env_lock_owner_and_candidate_signal_after_r12_no_patch_no_start_no_stop_no_kill_no_delete_no_order_20260521_125603_audit.json
run/audits/B1-PROFIT-LIVE-R37G_PROVIDER_RUNTIME_SELECTED_OPTION_MISMATCH_AUDIT_NO_ORDER_audit_dhan_unavailable_vs_zerodha_selected_option_flow_no_patch_no_start_no_order_20260527_000306/recent_provider_lines.txt
run/audits/B1-PROFIT-LIVE-R37G_PROVIDER_RUNTIME_SELECTED_OPTION_MISMATCH_AUDIT_NO_ORDER_audit_dhan_unavailable_vs_zerodha_selected_option_flow_no_patch_no_start_no_order_20260527_000306/redis_provider_health_keys.txt
run/audits/B1-PROFIT-LIVE-R37G_PROVIDER_RUNTIME_SELECTED_OPTION_MISMATCH_AUDIT_NO_ORDER_audit_dhan_unavailable_vs_zerodha_selected_option_flow_no_patch_no_start_no_order_20260527_000306/redis_provider_health_values.txt
run/audits/B1-PROFIT-LIVE-R38E_PREOPEN_LIVE_OBSERVE_READINESS_RUNBOOK_NO_PATCH_NO_START_NO_ORDER_freeze_tomorrow_observe_only_to_controlled_paper_gate_after_provider_fallback_patch_20260528_222506_report.md
run/audits/B1-PROFIT-LIVE-R38X-R2_strict_json_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_195424_report.md
run/audits/B1-PROFIT-LIVE-R38X_offline_sealed_export_candidate_audit_no_patch_no_order_no_paper_20260531_194922_report.md
run/audits/B1-PROFIT-LIVE-R38ZH-R2_offline_patched_candidate_reevaluation_after_stale_feed_cleanup_no_patch_no_order_20260531_225914_report.md
run/audits/B1-PROFIT-LIVE-R39C_A7_PROVIDER_RUNTIME_COMPAT_SEAM_AUDIT_NO_PATCH_NO_START_NO_STOP_NO_ORDER_find_exact_strategy_consumer_provider_runtime_missing_keys_patch_seam_after_r39b_20260602_093956_report.md
run/audits/B1-PROFIT-LIVE-R39D_A7_POST_R39C_ERROR_FRESHNESS_AND_CAPTURE_CONTINUITY_NO_PATCH_NO_START_NO_STOP_NO_ORDER_prove_whether_provider_runtime_error_is_still_new_before_live_patch_20260602_094140_report.md
run/audits/B1-PROFIT-LIVE-R39J_A7_CONTROLLED_GENERIC_MAIN_REFRESH_LOAD_R39H_PATCH_NO_PAPER_NO_ORDER_graceful_observe_only_refresh_to_load_contracts_provider_runtime_patch_20260602_100032_report.md
run/audits/B1-PROFIT-LIVE-R39W8_NO_CANDIDATE_SCORE_GAP_BLOCKER_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_final_pobserve_candidate_absence_by_family_branch_score_gap_and_real_blocker_distribution_20260603_115326_raw/extracted_bundle/A7-POBSERVEPRINT_bundle_latest_pobserve_window_for_chatgpt_upload_no_patch_no_order_20260603_112346_proof.json
run/audits/B1-PROFIT-LIVE-R39W8_NO_CANDIDATE_SCORE_GAP_BLOCKER_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_final_pobserve_candidate_absence_by_family_branch_score_gap_and_real_blocker_distribution_20260603_115326_raw/extracted_bundle/A7-POBSERVEPRINT_bundle_latest_pobserve_window_for_chatgpt_upload_no_patch_no_order_20260603_112346_report.md
run/audits/B1-PROFIT-LIVE-R3_CLASSIC_READY_BLOCKER_EXTRACTION_NO_ORDER_extract_why_provider_ready_classic_rows_still_no_candidate_no_patch_no_start_no_kill_no_delete_no_order_20260521_094952_audit.json
run/audits/B1-PROFIT-LIVE-R3_CLASSIC_READY_BLOCKER_EXTRACTION_NO_ORDER_extract_why_provider_ready_classic_rows_still_no_candidate_no_patch_no_start_no_kill_no_delete_no_order_20260521_094952_classic_ready_blocker_report.md
run/audits/B1-PROFIT-LIVE-R4_CLASSIC_CANDIDATE_PATH_SOURCE_REVIEW_NO_ORDER_inspect_activation_safe_to_promote_zero_and_empty_selected_family_path_no_patch_no_start_no_kill_no_delete_no_order_20260521_095224_classic_candidate_path_source_review.md
run/audits/B1-PROFIT-LIVE-R6_CLASSIC_RUNTIME_ENABLEMENT_PATCH_PLAN_NO_PATCH_NO_ORDER_plan_narrow_observe_only_classic_runtime_candidate_enablement_after_r5_no_patch_no_start_no_order_20260521_100157_audit.json
run/audits/B1-PROFIT-LIVE-R6_CLASSIC_RUNTIME_ENABLEMENT_PATCH_PLAN_NO_PATCH_NO_ORDER_plan_narrow_observe_only_classic_runtime_candidate_enablement_after_r5_no_patch_no_start_no_order_20260521_100157_classic_runtime_enablement_plan_report.md
run/audits/B1-PROFIT-R1_OPTION_CONTEXT_AND_CANDIDATE_GENERATION_BLOCKER_AUDIT_NO_ORDER_audit_dhan_option_context_provider_readiness_and_no_candidate_causes_no_patch_no_start_no_order_20260520_145726_audit.json
run/audits/B1-PROFIT-R1_OPTION_CONTEXT_AND_CANDIDATE_GENERATION_BLOCKER_AUDIT_NO_ORDER_audit_dhan_option_context_provider_readiness_and_no_candidate_causes_no_patch_no_start_no_order_20260520_145726_option_context_candidate_blocker_report.md
run/audits/B1-PROFIT-R2_DHAN_OPTION_CONTEXT_RESTORE_OR_DEGRADE_ROUTE_PLAN_NO_ORDER_plan_restore_dhan_option_context_or_degraded_candidate_generation_route_no_patch_no_start_no_order_20260520_150536_audit.json
run/audits/B1-PROFIT-R2_DHAN_OPTION_CONTEXT_RESTORE_OR_DEGRADE_ROUTE_PLAN_NO_ORDER_plan_restore_dhan_option_context_or_degraded_candidate_generation_route_no_patch_no_start_no_order_20260520_150536_route_plan_report.md
run/audits/B3-R31_REPLAY_EXPORT_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_exact_artifacts_py_patch_for_candidate_blocker_economics_family_side_exports_20260531_195140_audit.json
run/audits/B3-R31_REPLAY_EXPORT_PATCH_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_plan_exact_artifacts_py_patch_for_candidate_blocker_economics_family_side_exports_20260531_195140_patch_plan.json
run/audits/B3-R32_REPLAY_ANALYSIS_EXPORTS_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER_patch_artifacts_py_add_candidate_blocker_economics_family_side_exports_compile_only_20260531_210853_audit.json
run/audits/B3-R32_REPLAY_ANALYSIS_EXPORTS_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER_patch_artifacts_py_add_candidate_blocker_economics_family_side_exports_compile_only_20260531_210853_patch.diff
run/audits/B3-R39_REPLAY_EXPORT_CONTENT_REVIEW_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_summarize_candidate_blocker_economics_family_side_exports_from_r37_without_replay_or_patch_20260531_213316_audit.json
run/audits/B3-R42_ECONOMICS_EXPORT_ENRICHMENT_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_review_r41_authority_candidates_and_freeze_safe_economics_summary_enrichment_design_20260531_214734_patch_plan.json
run/audits/B3-R55_AGGREGATE_HELPER_FILE_DISCOVERY_PATCH_PLAN_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_plan_fix_for_r53_helper_to_discover_candidate_audit_at_run_root_and_other_exports_in_artifacts_dir_20260531_232020_patch_plan.json
run/audits/B3-R56_AGGREGATE_HELPER_FILE_DISCOVERY_ONE_FILE_PATCH_NO_REDIS_NO_REPLAY_NO_ORDER_patch_artifacts_py_helper_to_find_candidate_audit_at_run_root_and_exports_in_artifacts_dir_20260531_232300_audit.json
run/audits/B3-R56_AGGREGATE_HELPER_FILE_DISCOVERY_ONE_FILE_PATCH_NO_REDIS_NO_REPLAY_NO_ORDER_patch_artifacts_py_helper_to_find_candidate_audit_at_run_root_and_exports_in_artifacts_dir_20260531_232300_patch.diff
run/audits/B4-DAY3-R2_LIVE_CONSUMER_VIEW_AND_CONTRACT_ERROR_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_running_generic_main_env_selected_option_consumer_surfaces_decisions_and_feature_family_contract_errors_20260603_095141_report.md
run/audits/B4-DAY3-R4C_R39WM_R2_COMPILE_FAIL_ROLLBACK_NO_START_NO_ORDER_restore_features_py_from_pre_r39wm_r2_backup_after_indentation_error_20260603_222947_raw.txt
run/audits/B4-DAY3-R4C_R39WM_R2_COMPILE_FAIL_ROLLBACK_NO_START_NO_ORDER_restore_features_py_from_pre_r39wm_r2_backup_after_indentation_error_20260603_222947_report.md
run/audits/LANE-X-DASH-R1_dashboard_lane_evidence_bundle_no_patch_no_order_20260604_230829_filelist.txt
run/audits/LANE-X-DASH-R1_dashboard_lane_evidence_bundle_no_patch_no_order_20260604_230829_raw.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_dashboard_source_audit.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_lane_x_proof_chain.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_report.md
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_safety_state.txt
run/audits/LANE-X-DASH-R2A_SOURCE_AUDIT_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_r3h_lite_source_lane_x_inputs_and_patch_needles_20260604_231059_shadow_near_candidate_output.txt
run/audits/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421_report.md
run/audits/LANE-X-DASH-R2B-CONFIRM_READ_ONLY_AFTER_CUT_PATCH_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_confirm_whether_cut_r2b_patch_changed_dashboard_source_or_not_20260604_231421_source_audit.txt
run/audits/LANE-X-R12_day4_evidence_index_no_patch_no_order_20260604_203314_raw.txt
run/audits/LANE-X-R13_sealed_data_integrity_audit_no_patch_no_replay_no_order_20260604_203422_raw.txt
run/audits/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712_raw.txt
run/audits/LANE-X-R14_candidate_promotion_audit_no_patch_no_replay_no_order_20260604_203712_report.md
run/audits/LANE-X-R15_misb_shelf_width_distribution_audit_no_patch_no_replay_no_order_20260604_203827_raw.txt
run/audits/LANE-X-R15_misb_shelf_width_distribution_audit_no_patch_no_replay_no_order_20260604_203827_report.md
run/audits/LANE-X-R16_mist_response_futures_impulse_audit_no_patch_no_replay_no_order_20260604_204031_raw.txt
run/audits/LANE-X-R16_mist_response_futures_impulse_audit_no_patch_no_replay_no_order_20260604_204031_report.md
run/audits/LANE-X-R17_snapshot_sync_view_data_invalid_audit_no_patch_no_replay_no_order_20260604_204256_raw.txt
run/audits/LANE-X-R17_snapshot_sync_view_data_invalid_audit_no_patch_no_replay_no_order_20260604_204256_report.md
run/audits/LANE-X-R18_dhan_miso_unavailable_audit_no_patch_no_replay_no_order_20260604_205403_raw.txt
run/audits/LANE-X-R18_dhan_miso_unavailable_audit_no_patch_no_replay_no_order_20260604_205403_report.md
run/audits/LANE-X-R19A_helper_source_locator_no_patch_no_order_20260604_205537_raw.txt
run/audits/LANE-X-R19A_helper_source_locator_no_patch_no_order_20260604_205537_report.md
run/audits/LANE-X-R19B_pcheck_disk_emoji_helper_patch_no_order_20260604_205659_raw.txt
run/audits/LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815_raw.txt
run/audits/LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815_report.md
run/audits/LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936_raw.txt
run/audits/LANE-X-R20_day4_consolidated_milestone_and_tomorrow_plan_no_patch_no_order_20260604_210132_raw.txt
run/audits/LANE-X-R21_family_strategy_source_review_bundle_no_patch_no_order_20260604_211329_filelist.txt
run/audits/LANE-X-R21_family_strategy_source_review_bundle_no_patch_no_order_20260604_211329_raw.txt
run/audits/LANE-X-R22A_mist_micro_option_response_source_seam_audit_no_patch_no_order_20260604_211933_raw.txt
run/audits/LANE-X-R22A_mist_micro_option_response_source_seam_audit_no_patch_no_order_20260604_211933_report.md
run/audits/LANE-X-R22B-DIAG_micro_option_response_context_no_patch_no_order_20260604_224928_raw.txt
run/audits/LANE-X-R22B-DIAG_micro_option_response_context_no_patch_no_order_20260604_224928_report.md
run/audits/LANE-X-R22B_micro_option_response_producer_patch_no_start_no_order_20260604_224759_raw.txt
run/audits/LANE-X-R22D_micro_option_response_patch_finalizer_tomorrow_live_validation_no_start_no_order_20260604_225437_raw.txt
run/audits/LANE-X-R23_post_r22_micro_response_evidence_bundle_no_patch_no_order_20260604_225905_filelist.txt
run/audits/LANE-X-R23_post_r22_micro_response_evidence_bundle_no_patch_no_order_20260604_225905_raw.txt
run/audits/LANE-X-R24A_opportunity_expansion_source_seam_audit_no_patch_no_order_20260604_230020_raw.txt
run/audits/LANE-X-R24A_opportunity_expansion_source_seam_audit_no_patch_no_order_20260604_230020_report.md
run/audits/LANE-X-R24C_post_r24b_shadow_near_candidate_finalizer_no_patch_no_order_20260604_230456_raw.txt
run/audits/LANE-X-R25B_friday_observe_only_start_or_reuse_no_patch_no_order_20260605_091243_raw.txt
run/audits/LANE-X-R25C_features_strategy_stale_log_triage_no_start_no_stop_no_patch_no_order_20260605_091725_raw.txt
run/audits/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342_raw.txt
run/audits/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342_report.txt
run/audits/LANE-X-R25G_live_r22_r24_micro_response_shadow_validator_no_patch_no_order_20260605_092342_shadow_near_candidate.json
run/audits/LANE-X-R25H_feature_consumer_view_provider_ready_inspector_no_patch_no_order_20260605_092458_raw.txt
run/audits/LANE-X-R25H_feature_consumer_view_provider_ready_inspector_no_patch_no_order_20260605_092458_report.txt
run/audits/LANE-X-R25J_rolling_r22_snapshot_tradability_sampler_no_patch_no_order_20260605_093000_raw.txt
run/audits/LANE-X-R25J_rolling_r22_snapshot_tradability_sampler_no_patch_no_order_20260605_093000_samples.csv
run/audits/LANE-X-R25K_futures_source_inventory_after_fut_missing_pcheck_no_patch_no_order_20260605_095301_raw.txt
run/audits/LANE-X-R25L_option_side_role_consistency_sampler_no_patch_no_order_20260605_095512_raw.txt
run/audits/LANE-X-R25L_option_side_role_consistency_sampler_no_patch_no_order_20260605_095512_samples.csv
run/audits/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_104251_raw.txt
run/audits/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_104251_samples.csv
run/audits/LANE-X-R25M-R2_corrected_invalid_member_anomaly_sampler_no_patch_no_order_20260605_105944_raw.txt
run/audits/LANE-X-R25M_invalid_member_anomaly_clamped_sampler_no_patch_no_order_20260605_101117_raw.txt
run/audits/LANE-X-R25M_invalid_member_anomaly_clamped_sampler_no_patch_no_order_20260605_101117_samples.csv
run/audits/LANE-X-R25N_shadow_opportunity_snapshot_freeze_no_patch_no_order_20260605_134052_raw.txt
run/audits/LANE-X-R25N_shadow_opportunity_snapshot_freeze_no_patch_no_order_20260605_134052_report.txt
run/audits/LANE-X-R25N_valid_frame_family_opportunity_sampler_no_patch_no_order_20260605_110051_raw.txt
run/audits/LANE-X-R25N_valid_frame_family_opportunity_sampler_no_patch_no_order_20260605_110051_samples.csv
run/audits/LANE-X-R25O_candidate_promotion_gap_inspector_no_patch_no_order_20260605_110846_raw.txt
run/audits/LANE-X-R25O_candidate_promotion_gap_inspector_no_patch_no_order_20260605_110846_report.txt
run/audits/LANE-X-R25O_day5_pseal_completion_finalizer_no_patch_no_order_20260605_152150_raw.txt
run/audits/LANE-X-R25P_day5_compact_evidence_bundle_no_patch_no_order_20260605_152449_filelist.txt
run/audits/LANE-X-R25P_day5_compact_evidence_bundle_no_patch_no_order_20260605_152449_raw.txt
run/audits/LANE-X-R25P_mist_futures_impulse_gap_inspector_no_patch_no_order_20260605_111037_raw.txt
run/audits/LANE-X-R25P_mist_futures_impulse_gap_inspector_no_patch_no_order_20260605_111037_report.txt
run/audits/LANE-X-R25Q_mist_futures_impulse_predicate_source_audit_no_patch_no_order_20260605_111859_raw.txt
run/audits/LANE-X-R25Q_mist_futures_impulse_predicate_source_audit_no_patch_no_order_20260605_111859_report.md
run/audits/LANE-X-R25R_futures_kinetic_primitive_gap_sampler_no_patch_no_order_20260605_112133_raw.txt
run/audits/LANE-X-R25R_futures_kinetic_primitive_gap_sampler_no_patch_no_order_20260605_112133_samples.csv
run/audits/LANE-X-R25S_futures_kinetic_producer_source_locator_no_patch_no_order_20260605_112757_raw.txt
run/audits/LANE-X-R25S_futures_kinetic_producer_source_locator_no_patch_no_order_20260605_112757_report.md
run/audits/LANE-X-R25T_readonly_hypothetical_futures_kinetics_from_raw_ticks_no_patch_no_order_20260605_113952_raw.txt
run/audits/LANE-X-R25T_readonly_hypothetical_futures_kinetics_from_raw_ticks_no_patch_no_order_20260605_113952_report.txt
run/audits/LANE-X-R26A_day5_bundle_root_cause_freeze_no_patch_no_order_20260607_112913_raw.txt
run/audits/LANE-X-R26A_day5_bundle_root_cause_freeze_no_patch_no_order_20260607_112913_report.md
run/audits/LANE-X-R26B_micro_futures_kinetics_producer_patch_no_start_no_order_20260607_113211_raw.txt
run/audits/LANE-X-R26C_micro_futures_kinetics_mist_consumer_selftest_no_patch_no_order_20260607_113339_raw.txt
run/audits/LANE-X-R26C_micro_futures_kinetics_mist_consumer_selftest_no_patch_no_order_20260607_113339_report.md
run/audits/LANE-X-R26D-R2_corrected_redisraw_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113823_raw.txt
run/audits/LANE-X-R26D-R2_corrected_redisraw_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113823_report.md
run/audits/LANE-X-R26D-R3_preserve_blank_values_redisraw_futures_kinetics_validator_no_patch_no_order_20260607_114851_raw.txt
run/audits/LANE-X-R26D-R3_preserve_blank_values_redisraw_futures_kinetics_validator_no_patch_no_order_20260607_114851_report.md
run/audits/LANE-X-R26D-R4_chronological_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_115028_raw.txt
run/audits/LANE-X-R26D-R4_chronological_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_115028_report.md
run/audits/LANE-X-R26D_day5_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113438_raw.txt
run/audits/LANE-X-R26D_day5_sealed_micro_futures_kinetics_validator_no_patch_no_order_20260607_113438_report.md
run/audits/LANE-X-R26E_micro_futures_kinetics_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_115137_raw.txt
run/audits/LANE-X-R26E_micro_futures_kinetics_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_115137_report.md
run/audits/LANE-X-R26F_micro_futures_kinetics_chain_evidence_bundle_no_patch_no_order_20260607_115245_filelist.txt
run/audits/LANE-X-R26F_micro_futures_kinetics_chain_evidence_bundle_no_patch_no_order_20260607_115245_raw.txt
run/audits/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657_raw.txt
run/audits/LANE-X-R27A_misb_shelf_validation_root_cause_audit_no_patch_no_order_20260607_115657_report.md
run/audits/LANE-X-R27B_misb_shelf_width_scale_window_audit_no_patch_no_order_20260607_115937_raw.txt
run/audits/LANE-X-R27B_misb_shelf_width_scale_window_audit_no_patch_no_order_20260607_115937_report.md
run/audits/LANE-X-R27C_misb_shelf_threshold_scenario_quality_audit_no_patch_no_order_20260607_120106_raw.txt
run/audits/LANE-X-R27C_misb_shelf_threshold_scenario_quality_audit_no_patch_no_order_20260607_120106_report.md
run/audits/LANE-X-R27D_misb_current_inclusive_shelf_reference_audit_no_patch_no_order_20260607_120243_raw.txt
run/audits/LANE-X-R27D_misb_current_inclusive_shelf_reference_audit_no_patch_no_order_20260607_120243_report.md
run/audits/LANE-X-R27E_misb_prior_shelf_breakout_ref_patch_no_start_no_order_20260607_120500_raw.txt
run/audits/LANE-X-R27F_sealed_prior_shelf_ref_contract_passthrough_validator_no_patch_no_order_20260607_120622_raw.txt
run/audits/LANE-X-R27F_sealed_prior_shelf_ref_contract_passthrough_validator_no_patch_no_order_20260607_120622_report.md
run/audits/LANE-X-R27G_misb_prior_shelf_ref_contract_passthrough_patch_no_start_no_order_20260607_120850_raw.txt
run/audits/LANE-X-R27H_rerun_sealed_prior_ref_contract_passthrough_validator_no_patch_no_order_20260607_121008_raw.txt
run/audits/LANE-X-R27H_rerun_sealed_prior_ref_contract_passthrough_validator_no_patch_no_order_20260607_121008_report.md
run/audits/LANE-X-R27I_misb_prior_shelf_ref_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_121138_raw.txt
run/audits/LANE-X-R27I_misb_prior_shelf_ref_patch_chain_finalizer_monday_observe_ready_no_patch_no_order_20260607_121138_report.md
run/audits/LANE-X-R27J_misb_prior_shelf_ref_chain_evidence_bundle_no_patch_no_order_20260607_121241_filelist.txt
run/audits/LANE-X-R27J_misb_prior_shelf_ref_chain_evidence_bundle_no_patch_no_order_20260607_121241_raw.txt
run/audits/LANE-X-R28A_weekend_consolidated_finalizer_monday_observe_checklist_no_patch_no_order_20260607_121432_raw.txt
run/audits/LANE-X-R28A_weekend_consolidated_finalizer_monday_observe_checklist_no_patch_no_order_20260607_121432_report.md
run/audits/LANE-X-R28B_final_weekend_observe_ready_evidence_bundle_no_patch_no_order_20260607_121600_filelist.txt
run/audits/LANE-X-R28B_final_weekend_observe_ready_evidence_bundle_no_patch_no_order_20260607_121600_raw.txt
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_dhan_files_audit.txt
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_dhan_import_compile.log
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_pcheck_readonly.txt
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_process_snapshot.txt
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_provider_runtime_status.txt
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_redis_dhan_provider_keys.txt
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_report.md
run/audits/LANE-X-R30B_DHAN_CONTEXT_ROOT_CAUSE_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_dhan_context_config_import_provider_runtime_redis_errors_without_start_or_patch_20260607_141044_safety.txt
run/audits/batch30j_r5ak_selection_fingerprint_timestamp_source_audit_20260510_101621/patch_candidates.json
run/patches/B1-PROFIT-LIVE-R38Y_feature_view_invalid_root_cause_audit_whole_chain_patch_plan_no_order_no_paper_20260531_210755_candidate_patch.py
run/patches/B1-PROFIT-LIVE-R39E_A7_NARROW_PROVIDER_RUNTIME_COMPAT_ALIAS_PATCH_NO_START_NO_STOP_NO_ORDER_wrap_strategy_provider_runtime_validation_with_alias_backfill_after_r39d_new_error_20260602_095012_patch.md
run/patches/B1-PROFIT-LIVE-R39G_A7_PATCH_EXACT_PROVIDER_RUNTIME_VALIDATOR_SEAM_NO_START_NO_STOP_NO_ORDER_contracts_py_validate_provider_runtime_alias_backfill_after_r39f_exact_seam_20260602_095527_patch.md
run/patches/B1-PROFIT-LIVE-R39X_AFTERMARKET_FEATURE_CONSUMER_VIEW_FAILOVER_READINESS_AUDIT_NO_PATCH_NO_START_NO_ORDER_inspect_safe_to_consume_provider_ready_classic_tradability_and_failover_active_mapping_after_b3_r64b_20260602_225356_patch_plan.md
run/patches/B1-PROFIT-LIVE-R39Y_AFTERMARKET_CONSUMER_VIEW_READINESS_CONTEXT_MAP_NO_PATCH_NO_START_NO_ORDER_map_exact_safe_to_consume_data_valid_tradability_snapshot_sync_provider_ready_classic_sources_after_r39x_20260602_225636_patch_plan.md
run/patches/B1-PROFIT-LIVE-R39Z_AFTERMARKET_FAILOVER_ACTIVE_CONSUMER_VIEW_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_decide_contract_verdict_for_zerodha_failover_active_classic_provider_readiness_after_r39y_20260602_225848_patch_plan.md
run/patches/B1-PROFIT-LIVE-R6_CLASSIC_RUNTIME_ENABLEMENT_PATCH_PLAN_NO_PATCH_NO_ORDER_plan_narrow_observe_only_classic_runtime_candidate_enablement_after_r5_no_patch_no_start_no_order_20260521_100157_patch_plan.md
run/patches/B1-PROFIT-R2_DHAN_OPTION_CONTEXT_RESTORE_OR_DEGRADE_ROUTE_PLAN_NO_ORDER_plan_restore_dhan_option_context_or_degraded_candidate_generation_route_no_patch_no_start_no_order_20260520_150536_route_plan.md

## Replay baseline/shadow capability clue
FOUND bin/replay_run.py
FOUND bin/replay_compare.py
FOUND app/mme_scalpx/replay/differential.py
FOUND app/mme_scalpx/replay/overrides.py
FOUND app/mme_scalpx/replay/comparison_artifacts.py

CLASSIFICATION=PASS_R5A_PATCH_IMPACT_ROUTE_SURFACE_VISIBLE_READY_FOR_R5B_BASELINE_SHADOW_PLAN
