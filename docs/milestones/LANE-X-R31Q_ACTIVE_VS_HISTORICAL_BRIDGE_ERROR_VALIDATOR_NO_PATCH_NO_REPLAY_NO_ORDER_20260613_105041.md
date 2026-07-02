# LANE-X-R31Q_ACTIVE_VS_HISTORICAL_BRIDGE_ERROR_VALIDATOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_105041
2026-06-13T10:50:41+05:30

LAW=ACTIVE_ERROR_VALIDATOR_ONLY_NO_PATCH_NO_REPLAY_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31P proof
R31P=run/proofs/LANE-X-R31P_TARGETED_COMMON_KEYS_CONTRACT_STATUS_TEST_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104723.json
{
  "tag": "LANE-X-R31P_TARGETED_COMMON_KEYS_CONTRACT_STATUS_TEST_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104723",
  "classification": "PASS_R31P_COMMON_KEYS_SEAM_NOT_PROVEN_OPEN_NEEDS_TARGETED_RUNTIME_VALIDATION",
  "patch_applied": false,
  "replay_executed": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "status_rc": "0",
  "compile_rc": "0",
  "import_rc": "0",
  "report": "run/audits/LANE-X-R31P_TARGETED_COMMON_KEYS_CONTRACT_STATUS_TEST_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104723_report.md"
}

## Safety
ACTIVE_RUNTIME_PROCESSES=NONE
orders_stream_len=0
risk_stream_len=0
execution_stream_len=0

## Active-vs-historical bridge/error audit
{
  "bridge_error_recent_90min": 0,
  "bridge_error_total_in_sample": 0,
  "common_key_error_recent_90min": 0,
  "common_key_error_total_in_sample": 0,
  "decision_actions": {
    "HOLD": 300
  },
  "decision_top_reasons": {
    "hold_only_family_features_consumer_bridge": 300
  },
  "decisions_sampled": 300,
  "errors_sampled": 300,
  "features_sampled": 100,
  "interpretation": {
    "bridge_hold_reason_active_in_decisions": true,
    "r31_common_key_seam_active_now": false
  },
  "latest_bridge_error": null,
  "latest_common_key_error": null,
  "latest_decision": {
    "action": "HOLD",
    "activation_candidate_count": "0",
    "age_min": 57326.1,
    "data_valid": "0",
    "hold_only": "1",
    "id": "1777888475610-0",
    "provider_ready_classic": "0",
    "reason": "hold_only_family_features_consumer_bridge",
    "safe_to_consume": "1"
  },
  "now_ms": 1781328041829
}
AUDIT_RC=0

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
CLASSIFICATION=PASS_R31Q_COMMON_KEY_ERROR_NOT_ACTIVE_NO_R31_PATCH_REQUIRED
