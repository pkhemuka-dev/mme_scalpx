# 26-O23-Q-R14-R1 — projection failure diagnostic

Final verdict: `PASS_O23_Q_R14_R1_PROJECTION_FAILURE_DIAGNOSED_NO_SOURCE_PATCH`

Diagnosis: `SYNTHETIC_HARNESS_DID_NOT_REACH_XADD_OR_PUBLISH_DECISION_SIGNATURE_MISMATCH`

This batch does not patch source. It imports the strategy module, inspects helper signatures, reproduces the failed projection path with original helpers, and repeats the test with flexible diagnostic helpers to identify whether the Q-R13 projection block is swallowing a helper/signature exception.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_precheck.json`
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_helper_signature_audit.json`
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_original_helper_projection_test.json`
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_flexible_helper_projection_test.json`
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_source_projection_snippet.json`
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_r1_projection_failure_diagnostic_20260510_131701/o23q_r14_r1_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_r1_projection_failure_diagnostic.json`
- `run/proofs/proof_batch26o23_q_r14_r1_projection_failure_diagnostic_latest.json`

Next:
26-O23-Q-R14-R2 correct synthetic harness only; no source patch.
