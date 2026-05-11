# 26-O23-Q-R20-R1 — live-session rerun package

Final verdict: `PASS_O23_Q_R20_R1_MARKET_CLOSED_BLOCK_CLASSIFIED_RERUN_READY`

Q-R20 was blocked because it was run outside live market hours. This is not a source failure and not a safety failure.

## Re-run condition

Run Q-R20 only during a live market session after observe-only stack/current streams are already available.

## Expected PASS checks

- market_session_window_ok=true
- decision_inspection_ok=true
- rows_with_family_scope_candidates_json > 0
- projection_ok_rows > 0
- orders_growth=0
- orders_zero=true
- position_flat=true
- runtime_no_risk_execution_pids=true
- source_hash_unchanged=true

## Generated artifacts

- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_precheck.json`
- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_block_classification.json`
- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_live_session_rerun_command.txt`
- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_source_no_patch_proof.json`
- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_runtime_safety_readback.json`
- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_compile_import_proof.json`
- `run/live_capture/batch26o23_q_r20_r1_market_closed_classification_20260510_194720/o23q_r20_r1_final_summary.json`
- `run/proofs/proof_batch26o23_q_r20_r1_market_closed_classification.json`
- `run/proofs/proof_batch26o23_q_r20_r1_market_closed_classification_latest.json`

Controlled paper remains `BLOCKED_NO_EVIDENCE_BACKED_SCOPE`.
Real live remains `BLOCKED`.
