# B3-R31B_ARTIFACTS_PY_FUNCTION_SIGNATURE_CALLGRAPH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R31B_SIGNATURE_CALLGRAPH_READY_FOR_R32_PATCH`  
Created: `2026-05-31T19:58:01.060733+05:30`

## Target

`app/mme_scalpx/replay/artifacts.py`

## Patch shape

`ADD_B3_R32_HELPERS_AND_CALL_AFTER_EXISTING_MATERIALIZATION_WRITES`

## Existing writer surface

`{'has_write_csv_artifact': True, 'has_write_json_artifact': True, 'has_write_candidate_audit_csv': True, 'has_write_trade_log_csv': True}`

## Top materialization candidates

`[{'name': 'write_manifest', 'lineno': 192, 'end_lineno': 197, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_dataset_summary', 'lineno': 199, 'end_lineno': 205, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_scope_profile', 'lineno': 207, 'end_lineno': 217, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_integrity_report_placeholder', 'lineno': 219, 'end_lineno': 232, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_metrics_summary_placeholder', 'lineno': 234, 'end_lineno': 245, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_effective_inputs', 'lineno': 247, 'end_lineno': 256, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_effective_overrides_flat', 'lineno': 258, 'end_lineno': 266, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}, {'name': 'write_engine_result', 'lineno': 268, 'end_lineno': 275, 'score': 4, 'reasons': ['calls_write_json_artifact', 'name_write']}]`

## Safety

Signature/callgraph audit only. No Redis. No replay. No patch. No service action. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R31B_ARTIFACTS_PY_FUNCTION_SIGNATURE_CALLGRAPH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_extract_exact_writer_signatures_call_sites_and_safe_r32_patch_shape_20260531_195800.json`
- Latest proof: `run/proofs/B3_R31B_latest.json`
- Audit: `run/audits/B3-R31B_ARTIFACTS_PY_FUNCTION_SIGNATURE_CALLGRAPH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_extract_exact_writer_signatures_call_sites_and_safe_r32_patch_shape_20260531_195800_audit.json`
