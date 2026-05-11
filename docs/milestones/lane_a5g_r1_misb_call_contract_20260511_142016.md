# 26-O23-Q-A5G-R1 — MISB CALL Controlled-Paper Contract / No Order

Generated UTC: 2026-05-11T08:50:21.689162+00:00

## Final verdict

`BLOCKED_A5G_R1_MISB_CALL_CONTRACT_HAS_BLOCKERS`

## Classification

`BLOCKED`

## A5F acceptance

- A5F-R1 pass: True
- MISB CALL selected: False

## Contract

- Scope: MISB CALL, 1 lot
- Approval now: false
- Approval phrase recorded not consumed: true
- A5C/A5E approval reused: false
- Real live: blocked

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
  "A5F_BEST_SCOPE_NOT_MISB_CALL"
]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_A5G_R2_PREFLIGHT_A5G_R3_DRYCHECK_AND_FRESH_EXACT_APPROVAL",
  "REAL_LIVE_STILL_BLOCKED",
  "A5G_R1_IS_CONTRACT_ONLY_NOT_ENABLEMENT",
  "A5G_R1_DID_NOT_START_RISK_OR_EXECUTION",
  "A5G_R1_DID_NOT_CALL_BROKER",
  "A5G_R1_DID_NOT_PLACE_ORDER",
  "APPROVAL_PHRASE_RECORDED_NOT_CONSUMED"
]

## Next recommended batch

PAUSE_A5G_AND_REVIEW_BLOCKERS
