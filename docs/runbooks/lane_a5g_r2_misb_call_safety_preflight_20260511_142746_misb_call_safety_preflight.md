# 26-O23-Q-A5G-R2 — MISB CALL Safety Preflight

Generated UTC: 2026-05-11T09:02:41.258784+00:00

## Final verdict

`BLOCKED_A5G_R2_MISB_CALL_PREFLIGHT_HAS_BLOCKERS`

## Classification

`BLOCKED`

## Scope

- Family: MISB
- Side: CALL
- Quantity: 1 lot only
- Approval now: false

## Boundary

A5G-R2 is safety preflight only. It does not enable paper, start risk/execution, call broker, or place orders.

## Safety

- orders_zero: True
- orders_growth_5s: 0
- position_flat: True
- runtime_no_risk_execution_pids: True
- no_order_path_like_pids: True
- paper_live_broker_env_unset: True
- broker_calls_executed: false
- order_attempted: false
- paper_start_attempted: false
- real_live_attempted: false

## MISB CALL live evidence

- evidence_count: 27600
- candidate_count: 17850
- blocker_count: 21900
- no_trade_count: 21450

## Next

PAUSE_A5G_AND_REVIEW_BLOCKERS
