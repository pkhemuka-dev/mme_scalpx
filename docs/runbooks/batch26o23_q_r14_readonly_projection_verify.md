# 26-O23-Q-R14 — read-only decision-payload projection verification

Final verdict: `FAIL_O23_Q_R14_READONLY_PROJECTION_VERIFY_BLOCKED`

This batch performs a synthetic, read-only verification of `StrategyService.publish_decision` projection behavior using a fake Redis object and monkeypatched stream-field producer.

It does not start services, send broker orders, patch source, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_readonly_projection_verify_20260510_131358/o23q_r14_precheck.json`
- `run/live_capture/batch26o23_q_r14_readonly_projection_verify_20260510_131358/o23q_r14_synthetic_projection_test.json`
- `run/live_capture/batch26o23_q_r14_readonly_projection_verify_20260510_131358/o23q_r14_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r14_readonly_projection_verify_20260510_131358/o23q_r14_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_readonly_projection_verify_20260510_131358/o23q_r14_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r14_readonly_projection_verify_20260510_131358/o23q_r14_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_readonly_projection_verify.json`
- `run/proofs/proof_batch26o23_q_r14_readonly_projection_verify_latest.json`

Next:
Inspect Q-R14 synthetic projection failure; do not start services.
