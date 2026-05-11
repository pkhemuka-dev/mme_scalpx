# 26-O23-Q-R15-R2 — self-contained producer / consumer contract audit

Final verdict: `PASS_O23_Q_R15_R2_PRODUCER_ONLY_CONTRACT_AUDITED_NO_RUNTIME_CONSUMER`

This batch derives `family_scope_candidates_json` producer and consumer status directly from current source and repository scan.

It does not patch source, start services, write orders, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_precheck.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_source_producer_audit.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_repo_consumer_audit.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_ast_consumer_audit.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_field_contract.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r15_r2_selfcontained_audit_20260510_193113/o23q_r15_r2_final_summary.json`
- `run/proofs/proof_batch26o23_q_r15_r2_selfcontained_audit.json`
- `run/proofs/proof_batch26o23_q_r15_r2_selfcontained_audit_latest.json`

Next:
26-O23-Q-R16 read-only off-market strategy decision fixture with real stream-field validator/payload_json; no paper/live.
