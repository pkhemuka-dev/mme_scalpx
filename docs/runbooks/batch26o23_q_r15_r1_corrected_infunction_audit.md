# 26-O23-Q-R15-R1 — corrected in-function producer / consumer audit

Final verdict: `FAIL_O23_Q_R15_R1_PRECHECK_BLOCKED`

This batch corrects Q-R15 audit logic. It checks the producer contract within `StrategyService.publish_decision`, confirms consumer references, and does not patch source or start services.

Generated artifacts:
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_precheck.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_source_corrected_audit.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_repo_consumer_audit.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_ast_consumer_audit.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_field_contract.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r15_r1_corrected_infunction_audit_20260510_191747/o23q_r15_r1_final_summary.json`
- `run/proofs/proof_batch26o23_q_r15_r1_corrected_infunction_audit.json`
- `run/proofs/proof_batch26o23_q_r15_r1_corrected_infunction_audit_latest.json`

Next:
Fix Q-R15-R1 precheck false_keys; no paper/live.
