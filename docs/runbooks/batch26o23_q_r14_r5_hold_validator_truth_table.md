# 26-O23-Q-R14-R5 — HOLD validator truth table

Final verdict: `PASS_O23_Q_R14_R5_HOLD_VALIDATOR_DIAGNOSED_NO_SOURCE_PATCH`

Diagnosis: `NO_SYNTHETIC_DECISION_VARIANT_PASSED_HOLD_VALIDATOR_YET`

This batch does not patch source. It inspects the R14-R4 matrix errors, extracts `_validate_hold_decision_for_publish`, runs a validator truth table, and tests publish-path variants with fake Redis.

Generated artifacts:
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_precheck.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_q14_r4_error_extract.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_validator_contract.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_validator_truth_table.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_publish_truth_table.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r14_r5_hold_validator_truth_table_20260510_191004/o23q_r14_r5_final_summary.json`
- `run/proofs/proof_batch26o23_q_r14_r5_hold_validator_truth_table.json`
- `run/proofs/proof_batch26o23_q_r14_r5_hold_validator_truth_table_latest.json`

Next:
26-O23-Q-R14-R6 build exact decision fixture from real bridge/build_hold_decision output or inspect validator source for missing keys; no source patch.
