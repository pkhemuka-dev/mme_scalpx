# batch26o23_q_a5g_r0_miso_scope_eligibility_dhan_context_20260511_145912

Lane: A5G — MISO Controlled-Paper Scope Selector

Verdict: `PASS_A5G_R0_MISO_CALL_ELIGIBLE_READY_FOR_SCOPE_CONTRACT`

Next batch: `26-O23-Q-A5G-R1 MISO CALL controlled-paper scope contract / no order / no broker call`

This batch only inspects MISO eligibility and Dhan-context evidence.
No contract was written.

MISO:
- MISO_CALL eligible: True
- MISO_PUT matrix eligible: False
- MISO_PUT block reason: MISO_DHAN_CONTEXT_NOT_OBSERVED
- selected_scope: MISO:CALL
- selection_reason: MISO_CALL_MATRIX_ELIGIBLE

Dhan:
- dhan_context_present_readonly: False
- dhan_context_current_proven: False

Safety:
- source_patch_applied: false
- contract_written: false
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

Blockers:
- none
