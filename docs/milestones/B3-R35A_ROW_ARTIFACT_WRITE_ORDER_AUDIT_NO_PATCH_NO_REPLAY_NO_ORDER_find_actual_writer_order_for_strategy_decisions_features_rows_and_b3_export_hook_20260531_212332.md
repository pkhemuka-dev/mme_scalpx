# B3-R35A_ROW_ARTIFACT_WRITE_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R35A_ROW_ARTIFACT_WRITE_ORDER_ROOT_CAUSE_READY`  
Created: `2026-05-31T21:23:33.134448+05:30`

## Likely root cause

`B3_EXPORT_CALL_EXECUTES_BEFORE_STRATEGY_DECISIONS_AND_FEATURES_ROWS_ARE_WRITTEN`

## Row writer candidates

`[{'source': 'app/mme_scalpx/replay/artifacts.py', 'name': 'write_b3_r32_analysis_exports', 'lineno': 630, 'end_lineno': 679, 'score': 17, 'contains': ['features_rows.json', 'strategy_decisions.json', 'features_rows', 'strategy_decisions', 'write_b3_r32_analysis_exports', 'write_json_artifact', 'artifact_plan', 'artifacts_dir', 'export']}, {'source': 'app/mme_scalpx/replay/artifacts.py', 'name': '_b3_r32_write_economics_summary_export', 'lineno': 531, 'end_lineno': 579, 'score': 10, 'contains': ['features_rows', 'strategy_decisions', 'write_json_artifact', 'artifact_plan', 'artifacts_dir', 'export']}, {'source': 'bin/replay_run.py', 'name': 'main', 'lineno': 2894, 'end_lineno': 3067, 'score': 40, 'contains': ['features_rows.json', 'strategy_decisions.json', 'risk_outputs.json', 'execution_shadow_results.json', 'features_rows', 'strategy_decisions', 'write_core_artifact_bundle', 'artifact_plan', 'artifacts_dir', 'dump', 'write_text', 'json.dump']}, {'source': 'bin/replay_run.py', 'name': 'build_run_summary_payload', 'lineno': 2251, 'end_lineno': 2345, 'score': 2, 'contains': ['strategy_decisions', 'export']}, {'source': 'bin/replay_run.py', 'name': 'build_strategy_decisions_from_feature_frames', 'lineno': 1733, 'end_lineno': 1766, 'score': 1, 'contains': ['strategy_decisions']}, {'source': 'bin/replay_run.py', 'name': 'build_risk_outputs_from_strategy_decisions', 'lineno': 1794, 'end_lineno': 1829, 'score': 1, 'contains': ['strategy_decisions']}, {'source': 'bin/replay_run.py', 'name': 'build_persisted_strategy_decisions', 'lineno': 1974, 'end_lineno': 2102, 'score': 1, 'contains': ['strategy_decisions']}, {'source': 'bin/replay_run.py', 'name': 'build_persisted_risk_outputs', 'lineno': 2104, 'end_lineno': 2224, 'score': 1, 'contains': ['strategy_decisions']}, {'source': 'bin/replay_run.py', 'name': 'make_stage_executor', 'lineno': 2607, 'end_lineno': 2783, 'score': 1, 'contains': ['strategy_decisions']}, {'source': 'bin/replay_run.py', 'name': '__init__', 'lineno': 116, 'end_lineno': 121, 'score': 1, 'contains': ['strategy_decisions']}]`

## B3 call candidates

`[{'source': 'app/mme_scalpx/replay/artifacts.py', 'name': 'write_b3_r32_analysis_exports', 'lineno': 630, 'end_lineno': 679, 'score': 17, 'contains': ['features_rows.json', 'strategy_decisions.json', 'features_rows', 'strategy_decisions', 'write_b3_r32_analysis_exports', 'write_json_artifact', 'artifact_plan', 'artifacts_dir', 'export']}, {'source': 'app/mme_scalpx/replay/artifacts.py', 'name': 'write_core_artifact_bundle', 'lineno': 682, 'end_lineno': 733, 'score': 9, 'contains': ['write_b3_r32_analysis_exports', 'B3_R32_REPLAY_ANALYSIS_EXPORTS_CALL', 'write_core_artifact_bundle', 'artifact_plan', 'export']}]`

## Safety

Source/order audit only. No Redis. No replay. No patch. No service action. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R35A_ROW_ARTIFACT_WRITE_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_find_actual_writer_order_for_strategy_decisions_features_rows_and_b3_export_hook_20260531_212332.json`
- Latest proof: `run/proofs/B3_R35A_latest.json`
- Audit: `run/audits/B3-R35A_ROW_ARTIFACT_WRITE_ORDER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_find_actual_writer_order_for_strategy_decisions_features_rows_and_b3_export_hook_20260531_212332_audit.json`
