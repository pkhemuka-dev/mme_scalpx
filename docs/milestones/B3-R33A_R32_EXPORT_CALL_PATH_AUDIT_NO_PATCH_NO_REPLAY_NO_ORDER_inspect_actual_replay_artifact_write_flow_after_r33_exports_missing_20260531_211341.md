# B3-R33A_R32_EXPORT_CALL_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R33A_EXPORT_CALL_PATH_ROOT_CAUSE_READY`  
Created: `2026-05-31T21:13:41.969581+05:30`

## Likely root cause

`WRITE_CORE_ARTIFACT_BUNDLE_MAY_BE_USED_BUT_B3_EXPORT_CALL_NOT_CONFIRMED_IN_EXTERNAL_FLOW`

## External write_core_artifact_bundle calls

`[{'source': 'bin/replay_run.py', 'caller': 'main', 'caller_lineno': 2894, 'line': 2957, 'call': "writer.write_core_artifact_bundle(run_context, topology_plan, integrity_verdict=integrity_bundle.verdict.value, metrics={'stage_count': engine_result.stage_count})"}]`

## External B3 export calls

`[]`

## Safety

Call-path/source audit only. No Redis. No replay. No patch. No service action. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R33A_R32_EXPORT_CALL_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_actual_replay_artifact_write_flow_after_r33_exports_missing_20260531_211341.json`
- Latest proof: `run/proofs/B3_R33A_latest.json`
- Audit: `run/audits/B3-R33A_R32_EXPORT_CALL_PATH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_actual_replay_artifact_write_flow_after_r33_exports_missing_20260531_211341_audit.json`
