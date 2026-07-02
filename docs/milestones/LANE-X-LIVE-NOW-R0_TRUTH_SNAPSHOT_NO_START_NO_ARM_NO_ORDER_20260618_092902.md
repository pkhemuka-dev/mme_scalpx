# Lane X Live Now Truth Snapshot

- timestamp: 2026-06-18T09:29:02+05:30
- mode: NO_START_NO_ARM_NO_ORDER
- purpose: market-live truth check before any controlled-paper decision

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzgxNzU2OTA0LCJpYXQiOjE3ODE2NzA1MDQsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA5NjQ0NTQ2In0.nSn1rzBa13ojsnbDJD0B9QrcGDRJA6tEk5zHSWmlWoyBDvK3mLcosXUnsMwY6Viu552tumCaXcXrIMkWItpUSg
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1

## Time
Thu Jun 18 09:29:02 IST 2026

## Git dirty summary
 M app/mme_scalpx/ops_dashboard/server.py
 M app/mme_scalpx/replay/strategy_adapter.py
 M app/mme_scalpx/services/controlled_paper_route.py
 M app/mme_scalpx/services/controlled_paper_runtime.py
 M app/mme_scalpx/services/execution.py
 M app/mme_scalpx/services/feature_family/misb_surface.py
 M app/mme_scalpx/services/feature_family/misc_surface.py
 M app/mme_scalpx/services/feature_family/misr_surface.py
 M app/mme_scalpx/services/features.py
 M app/mme_scalpx/services/monitor.py
 M app/mme_scalpx/services/risk.py
 M app/mme_scalpx/services/strategy.py
 M app/mme_scalpx/services/strategy_family/common.py
 M bin/replay_run.py
 M bin/start_controlled_paper_runtime_chain.py
 M data/instruments/nfo_instruments.csv
?? $JSONL
?? $LOG
?? $PROOF
?? $RAW
?? $REPORT
?? app/mme_scalpx/replay/miv_research_evaluator.py
?? app/mme_scalpx/services/controlled_paper_runtime.py.r8m_backup_20260617_103053
?? app/mme_scalpx/services/controlled_paper_status_publication.py
?? app/mme_scalpx/services/execution.py.r10d_backup_LANE-X-R10D_IMPLEMENT_NOGROUP_REDIS_POLICY_POSITION_PSTATUS_PATCH_STATIC_ONLY_NO_START_NO_ORDER_20260617_220651
?? app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026
?? app/mme_scalpx/services/execution.py.r9i_backup_LANE-X-R9I_OFFLINE_PATCH_NOGROUP_RETRY_AND_MONITOR_LOCK_REFRESH_NO_START_NO_ORDER_20260617_131814
?? app/mme_scalpx/services/feature_family/misb_surface.py.r38ch_backup_20260616_112251
?? app/mme_scalpx/services/feature_family/misb_surface.py.r38cp_backup_20260616_141120
?? app/mme_scalpx/services/feature_family/misc_surface.py.r38dk_r1_backup_20260617_125027
?? app/mme_scalpx/services/feature_family/misr_surface.py.r38dl_backup_20260617_125224
?? app/mme_scalpx/services/monitor.py.r9i_backup_LANE-X-R9I_OFFLINE_PATCH_NOGROUP_RETRY_AND_MONITOR_LOCK_REFRESH_NO_START_NO_ORDER_20260617_131814
?? app/mme_scalpx/services/risk.py.r38x_backup_20260615_131026
?? app/mme_scalpx/services/risk.py.r8p_backup_20260617_103757
?? app/mme_scalpx/services/strategy.py.r34f_r1_backup
?? app/mme_scalpx/services/strategy.py.r34k_backup
?? app/mme_scalpx/services/strategy.py.r34m_backup
?? app/mme_scalpx/services/strategy.py.r38bx_backup_20260616_103514
?? app/mme_scalpx/services/strategy.py.r38bz_bad_patch_copy_20260616_103851
?? app/mme_scalpx/services/strategy_family/common.py.r38ct_backup_20260616_150737
?? app/mme_scalpx/services/strategy_family/common.py.r38cu_backup_20260616_151914
?? app/mme_scalpx/services/strategy_family/common.py.r38cw_backup_20260616_224313
?? app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py
?? app/mme_scalpx/services/strategy_family/misls.py
?? app/mme_scalpx/services/strategy_family/misls_input_extractor.py
?? app/mme_scalpx/services/strategy_family/misls_shadow_logger.py
?? app/mme_scalpx/services/strategy_family/miv_r_contract.py
?? bin/audit_miv_r1b_gate_surfaces_no_patch_no_replay_no_order.py
?? bin/audit_miv_r2b_evaluator_output_shape_no_patch_no_replay_no_order.py
?? bin/controlled_paper_status_publish
?? bin/lane_x_r32i_materialize_internal_order_intent_from_replay_results_no_broker.py
?? bin/lane_x_shadow_near_candidate_observer.py
?? bin/proof_miv_r1a_strategy_family_dormant_contract_no_replay_no_order.py
?? bin/proof_miv_r2_zerodha_lite_research_evaluator_no_replay_no_order.py
?? bin/proof_miv_r2c_neutral_label_route_no_patch_no_replay_no_order.py
?? bin/proof_r32d_internal_order_intent_pipeline_no_broker.py
?? bin/proof_r32g_real_candidate_hold_normalizer_no_broker.py
?? bin/pstatus
?? bin/pstatus.r10d_backup_LANE-X-R10D_IMPLEMENT_NOGROUP_REDIS_POLICY_POSITION_PSTATUS_PATCH_STATIC_ONLY_NO_START_NO_ORDER_20260617_220651
?? bin/r10i_tomorrow_combined_r10h_r38_preflight_no_start.sh
?? bin/r10j_tomorrow_one_lot_controlled_paper_wrapper_requires_fresh_approval.sh
?? bin/r10k_family_projection_readiness_board_no_start.sh
?? bin/r38dn_deep_decision_family_blocker_diag.py
?? bin/r38en_tomorrow_parallel_scope_controlled_paper_runner.sh
?? bin/r38eo_tomorrow_preflight_no_start.sh
?? bin/r38eq_controlled_paper_hard_gate.sh
?? bin/r38eq_tomorrow_hardened_preflight_no_start.sh
?? bin/start_controlled_paper_runtime_chain.py.r8m_backup_20260617_103053
?? bin/start_controlled_paper_runtime_chain.py.r8p_backup_20260617_103757
?? docs/contracts/LANE-X-CONTROLLED-PAPER-R5B_FREEZE_AND_R6_AFTERMARKET_PATCH_SCOPE_NO_PATCH_NO_ARM_NO_ORDER_20260616_133246_r6_patch_scope.md
?? docs/contracts/LANE-X-CONTROLLED-PAPER-R5G_R2_R6_PATCH_TARGET_DRILLDOWN_COMPACT_NO_PATCH_NO_ARM_NO_ORDER_20260616_151946_r6_exact_patch_targets.md
?? docs/contracts/LANE-X-CONTROLLED-PAPER-R5_RUNTIME_PUBLICATION_PATCH_PLAN_NO_PATCH_NO_ARM_NO_ORDER_20260616_121821_patch_plan.md
?? docs/contracts/LANE-X-LIVE-MISLS-RADAR-R2_TRAP_SHADOW_PATH_LOCATOR_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_101713_trap_shadow_path_contract.md
?? docs/contracts/LANE-X-LIVE-MISLS-RADAR-R3B_TRAP_SHADOW_VALUE_LOCATOR_DIRECT_REDIS_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_102531_trap_shadow_value_contract.md
?? docs/contracts/LANE-X-LIVE-MISLS-RADAR-R3C_COMPACT_VALUE_MAP_REVIEW_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_103203_compact_value_map_review_contract.md
?? docs/contracts/LANE-X-R38CS_CANDIDATE_METADATA_CONTRACT_REPAIR_PREFLIGHT_NO_ARM_NO_ORDER_20260616_144920_metadata_contract_repair_plan.md
?? docs/contracts/LANE-X-R38CW_AFTERMARKET_ALL_FAMILY_PAPER_READY_METADATA_CONTRACT_PATCH_NO_ARM_NO_ORDER_20260616_224313_tomorrow_live_paper_trial_plan.md
?? docs/contracts/LANE-X-R38CY_AFTERMARKET_FINAL_BLOCKER_SWEEP_FOR_TOMORROW_PAPER_NO_PATCH_NO_ARM_NO_ORDER_20260616_224735_tomorrow_go_no_go.md
?? docs/contracts/MISLS_AFTERMARKET_R0B_live_payload_path_map_contract.md
?? docs/contracts/MISLS_AFTERMARKET_R0C_exact_feature_payload_path_contract.md
?? docs/contracts/MISLS_R3_shadow_logger_surface_contract.md
?? docs/contracts/MISLS_R4B_shadow_logger_skeleton_contract.md
?? docs/contracts/MISLS_R4_shadow_logger_design_contract.md
?? docs/contracts/MISLS_R5B_signal_input_mapping_contract.md
?? docs/contracts/MISLS_R5C_read_only_input_extractor_contract.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_203023.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260615_153924.md
?? docs/milestones/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260616_143219.md
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
=== PROCESS SAFETY SNAPSHOT ===
=== PSTATUS CHECKS, IF AVAILABLE ===
=== EXISTING NO-START PREFLIGHT SCRIPTS FOUND ===
=== RUN EXISTING NO-START PREFLIGHT IF PRESENT ===
--- running r38eq_tomorrow_hardened_preflight_no_start.sh ---
r38eq_no_start_rc=0
=== POST-PREFLIGHT PROCESS SAFETY SNAPSHOT ===

## R0 verdict
REVIEW_LANE_X_LIVE_NOW_TRUTH_SNAPSHOT_COLLECTED_NO_START_NO_ARM_NO_ORDER

- r38eq_no_start_rc=0
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO

## Next decision
- If pstatus/no-start preflight says paper route allowed and flat/no broker/risk/execution gates are clean, then controlled-paper can be considered.
- If not, stay observe-only and fix only the shown blocker.
