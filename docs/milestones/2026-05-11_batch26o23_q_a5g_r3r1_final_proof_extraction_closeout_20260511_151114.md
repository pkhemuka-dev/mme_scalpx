# batch26o23_q_a5g_r3r1_final_proof_extraction_closeout_20260511_151114

Lane: A5G — A5G-R3 Final Proof Extraction Closeout

Verdict: `PASS_A5G_R3R1_NO_TRADE_SCOPE_SIGNAL_NOT_PRESENT_CLOSEOUT`

Next batch: `A5G MISO CALL first window complete as NO_TRADE; rerun later only if a new valid MISO CALL setup window is desired`

This batch did not rerun A5G-R3.
It only read the existing latest A5G-R3 proof and wrote a closeout classification.

A5G-R3 extracted:
- selected_scope: MISO:CALL
- final_verdict: MATERIAL_PASS_A5G_R3_CONTROLLED_PAPER_WINDOW_SAFE_NO_TRADE_SCOPE_SIGNAL_NOT_PRESENT
- final_pass: False
- material_pass: True
- controlled_paper_order_seen: False
- valid_miso_call_signal_seen: False
- no_order_candidate: True
- signal_seen_no_order: False
- orders_growth: 0
- position_flat_final: True
- risk_execution_stopped_final: True

Closeout result:
- result: NO_TRADE
- reason: SCOPE_SIGNAL_NOT_PRESENT

Safety now:
- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_call_attempted: false
- order_attempted: false
- redis_trading_stream_write_attempted: false
- orders_len_now: 0
- position_flat_now: True
- runtime_no_risk_execution_pids: True
- dangerous_env_unset_after: True

Artifacts:
- proof: run/proofs/proof_batch26o23_q_a5g_r3r1_final_proof_extraction_closeout.json
- latest: run/proofs/proof_batch26o23_q_a5g_r3r1_final_proof_extraction_closeout_latest.json
- result: run/live_controlled_paper/a5g/results/batch26o23_q_a5g_r3r1_final_proof_extraction_closeout_20260511_151114_NO_TRADE_SCOPE_SIGNAL_NOT_PRESENT.json
- latest result: run/live_controlled_paper/a5g/results/latest_A5G_R3R1_CLOSEOUT.json

Blockers:
- none
