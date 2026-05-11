# batch26o23_q_a5h_r3r1_market_window_block_closeout_20260511_152949

Lane: A5H — MISR CALL Market-Window Block Closeout

Verdict: `PASS_A5H_R3R1_MARKET_WINDOW_BLOCK_CLASSIFIED_SAFE_NO_ACTION`

Next batch: `STOP: A5H-R3 may be retried only in a valid market window with fresh exact A5H MISR CALL approval phrase`

This batch did not rerun A5H-R3.
It only classified the existing A5H-R3 proof.

A5H-R3 extracted:
- selected_scope: MISR:CALL
- final_verdict: BLOCKED_A5H_R3_CONTROLLED_PAPER_ORDER_CYCLE_NOT_SAFE_OR_INCOMPLETE
- blockers: ['MARKET_WINDOW_NOT_OPEN']
- market_window_ok: False
- approval_phrase_consumed: False
- preflight_ok: False
- service_start_attempted: False
- risk_execution_start_attempted: False
- broker_call_attempted: False
- real_live_attempted: False
- orders_growth: 0
- position_flat_final: True
- risk_execution_stopped_final: True

Closeout result:
- result: BLOCKED_NO_ACTION
- reason: MARKET_WINDOW_NOT_OPEN

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
- proof: run/proofs/proof_batch26o23_q_a5h_r3r1_market_window_block_closeout.json
- latest: run/proofs/proof_batch26o23_q_a5h_r3r1_market_window_block_closeout_latest.json
- result: run/live_controlled_paper/a5h/results/batch26o23_q_a5h_r3r1_market_window_block_closeout_20260511_152949_BLOCKED_NO_ACTION_MARKET_WINDOW_NOT_OPEN.json
- latest result: run/live_controlled_paper/a5h/results/latest_A5H_R3_MARKET_WINDOW_BLOCK_CLOSEOUT.json

Blockers:
- none
