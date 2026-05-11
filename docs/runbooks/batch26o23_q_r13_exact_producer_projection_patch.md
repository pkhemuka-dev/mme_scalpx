# 26-O23-Q-R13 — exact producer projection patch

Final verdict: `PASS_O23_Q_R13_EXACT_PRODUCER_PROJECTION_PATCH_COMPILE_IMPORT_OK`

This batch patches only `StrategyService.publish_decision` serialization to add `family_scope_candidates_json` into the active `decisions:mme:stream` XADD fields from `activation_report_json`.

It does not change strategy decisions, thresholds, candidate generation, risk, execution, position state, broker routing, paper, or live behavior.

Generated artifacts:
- `run/live_capture/batch26o23_q_r13_exact_producer_projection_patch_20260510_131122/o23q_r13_precheck.json`
- `run/live_capture/batch26o23_q_r13_exact_producer_projection_patch_20260510_131122/o23q_r13_patch_result.json`
- `run/live_capture/batch26o23_q_r13_exact_producer_projection_patch_20260510_131122/o23q_r13_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r13_exact_producer_projection_patch_20260510_131122/o23q_r13_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r13_exact_producer_projection_patch_20260510_131122/o23q_r13_source_state.json`
- `run/live_capture/batch26o23_q_r13_exact_producer_projection_patch_20260510_131122/o23q_r13_final_summary.json`
- `run/proofs/proof_batch26o23_q_r13_exact_producer_projection_patch.json`
- `run/proofs/proof_batch26o23_q_r13_exact_producer_projection_patch_latest.json`

Next:
26-O23-Q-R14 read-only decision-payload projection verification; no paper/live, no risk/execution.
