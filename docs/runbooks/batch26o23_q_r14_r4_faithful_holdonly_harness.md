# 26-O23-Q-R14-R4 — faithful HOLD-only publish harness verification

Final verdict: `FAIL_O23_Q_R14_R4_FAITHFUL_HOLDONLY_VERIFY_BLOCKED`

This batch uses `hold_only=1` decision mappings so `StrategyService.publish_decision` reaches the active XADD path and verifies the Q-R13 `family_scope_candidates_json` projection.

It does not patch source, start services, write orders, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_precheck.json`
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_helper_signature_audit.json`
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_faithful_holdonly_matrix.json`
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_source_snippet.json`
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r14_r4_faithful_holdonly_harness_20260510_190747/o23q_r14_r4_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_r4_faithful_holdonly_harness.json`
- `run/proofs/proof_batch26o23_q_r14_r4_faithful_holdonly_harness_latest.json`

Next:
Inspect faithful hold-only matrix errors; no source patch unless traceback proves source defect.
