# 26-O23-Q-R15 — source/consumer contract audit

Final verdict: `FAIL_O23_Q_R15_SOURCE_CONSUMER_AUDIT_BLOCKED`

This batch audits `family_scope_candidates_json` as a producer-side observation projection on `decisions:mme:stream`.

It does not patch source, start services, write orders, enable paper, or enable real live.

Generated artifacts:
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_precheck.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_source_audit.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_repo_occurrence_audit.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_ast_consumer_audit.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_field_contract.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r15_source_consumer_contract_audit_20260510_191609/o23q_r15_final_summary.json`
- `run/proofs/proof_batch26o23_q_r15_source_consumer_contract_audit.json`
- `run/proofs/proof_batch26o23_q_r15_source_consumer_contract_audit_latest.json`

Next:
Inspect Q-R15 consumer audit post_false_keys; do not proceed to runtime observe verification.
