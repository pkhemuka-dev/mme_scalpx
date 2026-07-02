# LANE-X-R31P_TARGETED_COMMON_KEYS_CONTRACT_STATUS_TEST_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104723
2026-06-13T10:47:23+05:30

LAW=TARGETED_CONTRACT_STATUS_TEST_ONLY_NO_PATCH_NO_REPLAY_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31O proof
R31O=run/proofs/LANE-X-R31O_DIRTY_TREE_OWNERSHIP_AND_R31_SEAM_STATUS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104524.json
{
  "tag": "LANE-X-R31O_DIRTY_TREE_OWNERSHIP_AND_R31_SEAM_STATUS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104524",
  "classification": "PASS_R31O_DIRTY_TREE_OWNERSHIP_MAP_READY_DECIDE_FREEZE_OR_TARGETED_TEST",
  "patch_applied": false,
  "replay_executed": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "audit_rc": "0",
  "compile_rc": "0",
  "import_rc": "0",
  "next_if_pass": "freeze_dirty_tree_or_run_targeted_contract_test_before_new_patch",
  "report": "run/audits/LANE-X-R31O_DIRTY_TREE_OWNERSHIP_AND_R31_SEAM_STATUS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104524_report.md"
}

## Safety
ACTIVE_RUNTIME_PROCESSES=NONE
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Targeted common-key contract status
{
  "actual_common_surfaces_seen": 100,
  "actual_exact_match_to_contract_seen": true,
  "actual_extra_keys_vs_contract": {},
  "actual_missing_keys_vs_contract": {},
  "actual_provider_key_sets_seen_count": 0,
  "contract_common_keys": [
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals"
  ],
  "contract_common_keys_count": 10,
  "feature_rows_sampled": 50,
  "provider_keys_in_contract_common_keys": [],
  "provider_keys_missing_from_contract_common_keys": [
    "active_futures_provider_id",
    "active_option_context_provider_id",
    "active_selected_option_provider_id",
    "family_runtime_mode"
  ],
  "r31_common_key_contract_status": "POSSIBLY_MOVED_PROVIDER_KEYS_OUT_OF_COMMON_OR_NO_RECENT_PROVIDER_COMMON_SURFACE",
  "sample_common_has_provider_keys": [],
  "sample_common_keys": [
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals"
  ],
  "sample_feature_id": "1777888201390-0",
  "source_has_common_exact_key_validator": true,
  "source_has_provider_runtime_validator": true
}
STATUS_RC=0

## Compile/import smoke
COMPILE_RC=0
{
  "app.mme_scalpx.replay.miv_research_evaluator": "OK",
  "app.mme_scalpx.replay.strategy_adapter": "OK",
  "app.mme_scalpx.services.feature_family.contracts": "OK",
  "app.mme_scalpx.services.features": "OK",
  "app.mme_scalpx.services.strategy": "OK",
  "app.mme_scalpx.services.strategy_family.decisions": "OK",
  "app.mme_scalpx.services.strategy_family.internal_order_intent_pipeline": "OK",
  "app.mme_scalpx.services.strategy_family.miv_r_contract": "OK"
}
IMPORT_RC=0

orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0
CLASSIFICATION=PASS_R31P_COMMON_KEYS_SEAM_NOT_PROVEN_OPEN_NEEDS_TARGETED_RUNTIME_VALIDATION
