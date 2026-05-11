# 26-O23-Q-R14-R3 — publish-path diagnostic

Final verdict: `PASS_O23_Q_R14_R3_PUBLISH_PATH_DIAGNOSED_NO_SOURCE_PATCH`

Diagnosis: `PUBLISH_PATH_RAISES_BEFORE_XADD_UNDER_SYNTHETIC_SERVICE_OBJECT`

This batch does not patch source. It reads the failed Q-R14-R2 artifact, reconstructs the projection locally, and runs granular `publish_decision` variants with fake Redis and fake validators.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_precheck.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_q14_r2_artifact_extract.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_helper_signature_audit.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_local_projection_reconstruction.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_publish_validate_any.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_publish_validate_keyword.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_publish_real_validate.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_source_publish_snippet.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_r3_publish_path_diagnostic_20260510_190155/o23q_r14_r3_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_r3_publish_path_diagnostic.json`
- `run/proofs/proof_batch26o23_q_r14_r3_publish_path_diagnostic_latest.json`

Next:
26-O23-Q-R14-R4 build faithful StrategyService test object or exact source repair only if source-backed by traceback.
