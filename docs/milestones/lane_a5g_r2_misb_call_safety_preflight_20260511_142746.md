# 26-O23-Q-A5G-R2 — MISB CALL Safety Preflight / No Order

Generated UTC: 2026-05-11T09:02:41.258784+00:00

## Final verdict

`BLOCKED_A5G_R2_MISB_CALL_PREFLIGHT_HAS_BLOCKERS`

## Classification

`BLOCKED`

## Contract acceptance

- A5F-R1 pass: True
- A5G-R1B pass: True
- Scope MISB CALL 1 lot unapproved: False

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

[
  "A5G_SCOPE_NOT_MISB_CALL_1LOT_UNAPPROVED"
]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_A5G_R3_DRYCHECK_AND_FRESH_EXACT_APPROVAL",
  "REAL_LIVE_STILL_BLOCKED",
  "A5G_R2_IS_SAFETY_PREFLIGHT_ONLY_NOT_ENABLEMENT",
  "A5G_R2_DID_NOT_START_RISK_OR_EXECUTION",
  "A5G_R2_DID_NOT_CALL_BROKER",
  "A5G_R2_DID_NOT_PLACE_ORDER",
  "APPROVAL_PHRASE_NOT_CONSUMED"
]

## Next recommended batch

PAUSE_A5G_AND_REVIEW_BLOCKERS
