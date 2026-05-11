# 26-O23-Q-A5H-R2 — One Controlled-Paper MISB CALL Order-Cycle

Generated UTC: 2026-05-11T09:53:54.625579+00:00

## Final verdict

`BLOCKED_A5H_R2_ORDER_CYCLE_FAIL_CLOSED_BEFORE_BROKER_CALL`

## Classification

`BLOCKED`

## Scope

- MISB CALL
- 1 lot only
- Paper/sandbox only
- Real live forbidden
- Broker failover forbidden

## Result

- order_attempted: False
- broker_calls_executed: False
- order_created: False
- order_sent: False

## Pre-order blockers

[
  "A5H_SCOPE_NOT_MISB_CALL_1LOT_PAPER_ONLY",
  "A5H_APPROVAL_GATE_NOT_ACCEPTED_OR_ALREADY_CONSUMED",
  "EXPLICIT_CONTROLLED_PAPER_ORDER_TOOL_NOT_FOUND_FAIL_CLOSED"
]

## Tool discovery

{
  "accepted_tool": null,
  "inspected_candidates": [],
  "candidate_count": 0,
  "accepted": false
}

## Safety before route

- orders_zero: True
- orders_growth_5s: 0
- position_flat: True
- runtime_no_risk_execution_pids: True
- no_order_path_like_pids: True
