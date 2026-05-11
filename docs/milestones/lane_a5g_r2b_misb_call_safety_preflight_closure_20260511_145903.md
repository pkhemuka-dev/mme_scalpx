# 26-O23-Q-A5G-R2B — MISB CALL Safety Preflight Closure / No Order

Generated UTC: 2026-05-11T09:29:54.898783+00:00

## Final verdict

`PASS_A5G_R2B_MISB_CALL_SAFETY_PREFLIGHT_CLOSED_NO_ENABLEMENT`

## Classification

`PASS`

## Contract acceptance

- A5F-R1 pass: True
- A5G-R1B pass: True
- Scope MISB CALL 1 lot unapproved: True

## Safety

- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_calls_executed: false
- order_attempted: false
- orders_zero: True
- position_flat: True
- runtime_no_risk_execution_pids: True
- paper_live_broker_env_unset: True

## Blockers

[]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_A5G_R3_DRYCHECK_AND_FRESH_EXACT_APPROVAL",
  "REAL_LIVE_STILL_BLOCKED",
  "A5G_R2B_IS_SAFETY_PREFLIGHT_CLOSURE_ONLY_NOT_ENABLEMENT",
  "A5G_R2B_DID_NOT_START_RISK_OR_EXECUTION",
  "A5G_R2B_DID_NOT_CALL_BROKER",
  "A5G_R2B_DID_NOT_PLACE_ORDER",
  "APPROVAL_PHRASE_NOT_CONSUMED"
]

## Next recommended batch

26-O23-Q-A5G-R3 MISB CALL guarded dry-check / no order
