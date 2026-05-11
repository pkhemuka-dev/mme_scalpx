# batch26o23_q_a5c_r3r1_no_trade_scope_signal_not_present_closeout_20260511_133811

Lane: A5C — First Controlled-Paper MIST CALL 1-Lot Gate

Verdict: `PASS_A5C_R3R1_NO_TRADE_SCOPE_SIGNAL_NOT_PRESENT_CLOSEOUT`

Next batch: `A5C controlled-paper first window complete as NO_TRADE; rerun A5C-R3 later only if a new valid MIST CALL setup window is desired`

Closeout result:
- result: NO_TRADE
- reason: SCOPE_SIGNAL_NOT_PRESENT
- valid_mist_call_signal_present: false
- controlled_paper_order_seen: false
- no_natural_order_candidate: true

Safety:
- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_call_attempted: false
- order_attempted: false
- redis_trading_stream_write_attempted: false
- orders_stream_zero: True
- position_flat: True
- runtime_no_risk_execution_pids: True

Artifacts:
- proof: run/proofs/proof_batch26o23_q_a5c_r3r1_no_trade_scope_signal_not_present_closeout.json
- latest: run/proofs/proof_batch26o23_q_a5c_r3r1_no_trade_scope_signal_not_present_closeout_latest.json
- result: run/live_controlled_paper/a5c/results/batch26o23_q_a5c_r3r1_no_trade_scope_signal_not_present_closeout_20260511_133811_NO_TRADE_SCOPE_SIGNAL_NOT_PRESENT.json
- latest result: run/live_controlled_paper/a5c/results/latest_NO_TRADE_SCOPE_SIGNAL_NOT_PRESENT.json

Blockers:
- none
