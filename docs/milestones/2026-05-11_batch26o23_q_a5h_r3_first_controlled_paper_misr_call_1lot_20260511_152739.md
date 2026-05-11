# batch26o23_q_a5h_r3_first_controlled_paper_misr_call_1lot_20260511_152739

Lane: A5H — First Controlled-Paper MISR CALL 1-Lot Gate

Verdict: `BLOCKED_A5H_R3_CONTROLLED_PAPER_ORDER_CYCLE_NOT_SAFE_OR_INCOMPLETE`

Next batch: `inspect blockers; do not rerun until resolved`

Scope:
- MISR CALL only
- 1 lot only
- paper/sandbox only
- real live forbidden
- broker failover forbidden
- mid-position provider migration forbidden
- MISR PUT not authorized in this contract
- no forced candidate
- no threshold relaxation
- no automatic strategy switching
- no all-5 order cycle

Safety:
- source_patch_applied: false
- real_live_attempted: false
- broker_call_attempted: false
- approval_phrase_consumed: False
- preflight_ok: False
- orders_before: 0
- orders_after_window: 0
- orders_final: 0
- orders_growth: 0
- position_flat_final: True
- risk_execution_stopped_final: True

Signal / order result:
- valid_misr_call_signal_seen: False
- controlled_paper_order_seen: False
- no_order_candidate: True
- signal_seen_no_order: False
- bad_order_scope_seen: False
- result_path: None

Blockers:
- MARKET_WINDOW_NOT_OPEN
