# A6-LIVE-R2I — Post-patch live activation-gate read-only probe

Generated IST: `2026-05-12T10:22:46.681106+05:30`

## Verdict

`BLOCKED_A6_LIVE_R2I_NO_LIVE_SCOPE_READY_YET_GATE_FAIL_CLOSED_NO_ORDER_NO_BROKER`

## Selected scope

`{'family_id': 'MISR', 'side': 'FLAT', 'branch_id': '', 'score': ''}`

## Gate result with env unset

- ok: `False`
- blockers: `['CONTROLLED_PAPER_RUNTIME_NOT_ENABLED', 'SCOPE_ACK_INVALID_OR_MISSING', 'SCOPE_ACK_MISMATCH', 'NO_ACTIVATION_CANDIDATE', 'ACTIVATION_SAFE_TO_PROMOTE_FALSE']`
- expected_blockers_present: `True`

## Paper readiness without env/ack

- preconditions_except_env_ack: `False`
- fresh_approval_phrase_required: `None`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-LIVE-R2 watcher rerun / wait for activation_safe_to_promote true`
