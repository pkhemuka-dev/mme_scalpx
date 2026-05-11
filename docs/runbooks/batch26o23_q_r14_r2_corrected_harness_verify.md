# 26-O23-Q-R14-R2 — corrected synthetic harness projection verification

Final verdict: `FAIL_O23_Q_R14_R2_CORRECTED_HARNESS_VERIFY_BLOCKED`

This batch corrects the synthetic harness only. It passes a mapping to `StrategyService.publish_decision` and uses the correct keyword-only validator signature.

It does not patch source, start services, send orders, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_r2_corrected_harness_verify_20260510_185327/o23q_r14_r2_precheck.json`
- `run/live_capture/batch26o23_q_r14_r2_corrected_harness_verify_20260510_185327/o23q_r14_r2_corrected_synthetic_projection_test.json`
- `run/live_capture/batch26o23_q_r14_r2_corrected_harness_verify_20260510_185327/o23q_r14_r2_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r14_r2_corrected_harness_verify_20260510_185327/o23q_r14_r2_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_r2_corrected_harness_verify_20260510_185327/o23q_r14_r2_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r14_r2_corrected_harness_verify_20260510_185327/o23q_r14_r2_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_r2_corrected_harness_verify.json`
- `run/proofs/proof_batch26o23_q_r14_r2_corrected_harness_verify_latest.json`

Next:
Inspect corrected synthetic projection artifacts; no service start.
