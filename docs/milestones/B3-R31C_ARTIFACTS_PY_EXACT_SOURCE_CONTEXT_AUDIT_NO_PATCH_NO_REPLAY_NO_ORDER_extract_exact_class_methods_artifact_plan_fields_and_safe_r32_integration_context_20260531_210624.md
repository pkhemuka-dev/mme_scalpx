# B3-R31C_ARTIFACTS_PY_EXACT_SOURCE_CONTEXT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R31C_EXACT_CONTEXT_READY_FOR_ONE_FILE_R32_PATCH`  
Created: `2026-05-31T21:06:24.514677+05:30`

## Target

`app/mme_scalpx/replay/artifacts.py`

## Writer owner class

`{'class': 'ReplayArtifactsWriter', 'lineno': 133, 'end_lineno': 372, 'methods': ['ensure_directories', 'write_json_artifact', 'write_csv_artifact', 'write_manifest', 'write_dataset_summary', 'write_scope_profile', 'write_integrity_report_placeholder', 'write_metrics_summary_placeholder', 'write_effective_inputs', 'write_effective_overrides_flat', 'write_engine_result', 'write_trade_log_csv', 'write_candidate_audit_csv', 'write_blocker_breakdown', 'write_exit_breakdown', 'write_differential_report', 'write_core_artifact_bundle']}`

## Artifact plan fields

`['artifacts_dir', 'blocker_breakdown_path', 'candidate_audit_path', 'dataset_summary_path', 'differential_report_path', 'effective_inputs_path', 'effective_overrides_flat_path', 'exit_breakdown_path', 'integrity_report_path', 'log_dir', 'manifest_path', 'metrics_summary_path', 'root_dir', 'scope_profile_path', 'trade_log_path']`

## Safety

Exact source-context audit only. No Redis. No replay. No patch. No service action. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R31C_ARTIFACTS_PY_EXACT_SOURCE_CONTEXT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_extract_exact_class_methods_artifact_plan_fields_and_safe_r32_integration_context_20260531_210624.json`
- Latest proof: `run/proofs/B3_R31C_latest.json`
- Audit: `run/audits/B3-R31C_ARTIFACTS_PY_EXACT_SOURCE_CONTEXT_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_extract_exact_class_methods_artifact_plan_fields_and_safe_r32_integration_context_20260531_210624_audit.json`
