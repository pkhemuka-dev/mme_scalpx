# 26-O23-Q-A5B-R1 — Controlled-Paper Safety Preflight / Read-Only Verification

Generated UTC: 2026-05-11T05:37:56.265106+00:00

## Final verdict

`BLOCKED_A5B_R1_CONTROLLED_PAPER_SAFETY_PREFLIGHT_HAS_BLOCKERS`

## Classification

`BLOCKED`

## Scope

Lane A5B is read-only safety preflight. It does not approve controlled paper and does not enable any order path.

## Evidence acceptance

- A3 Q-R21-R1 pass: False
- A3 Q-R20-R2 pass: False
- A4 R6B pass/material-pass: True
- A4 R3B pass/material-pass: True
- A4 R4 pass/material-pass: True

## Future candidate

- Scope: MIST_CALL
- Quantity: 1 lot
- Approval: false

## Current safety

- orders_zero: True
- orders_growth_5s: 0
- position_flat: True
- runtime_no_risk_execution_pids: True
- paper_live_broker_env_unset: True
- no_broker_like_pids: True
- source_patch_applied: false
- order_attempted: false
- broker_calls_executed: false
- paper_start_attempted: false
- real_live_attempted: false

## Readiness for A5C preflight

False

## Blockers

[
  "A3_Q_R21_R1_PASS_PROOF_NOT_FOUND_OR_NOT_ACCEPTED",
  "A3_Q_R20_R2_PASS_PROOF_NOT_FOUND_OR_NOT_ACCEPTED"
]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_A5A_CONTRACT_PASS_AND_EXPLICIT_USER_APPROVAL",
  "REAL_LIVE_STILL_BLOCKED",
  "A5B_R1_IS_READ_ONLY_PREFLIGHT_NOT_ENABLEMENT",
  "A5B_R1_DID_NOT_START_RISK_OR_EXECUTION",
  "A5B_R1_DID_NOT_CALL_BROKER",
  "A5B_R1_DID_NOT_PLACE_ORDER",
  "PRODUCER_ONLY_OBSERVATION_FIELD_IS_NOT_APPROVAL"
]

## Next recommended batch

26-O23-Q-A5B-R1B focused evidence/source/safety diagnostic / no enablement

## Artifacts

- Proof: `run/proofs/proof_lane_a5b_r1_controlled_paper_safety_preflight_20260511_110750.json`
- Latest proof: `run/proofs/proof_lane_a5b_r1_controlled_paper_safety_preflight_latest.json`
- Audit: `run/audits/lane_a5b_r1_controlled_paper_safety_preflight_20260511_110750.json`
- SHA256: `run/proofs/sha256_lane_a5b_r1_controlled_paper_safety_preflight_20260511_110750.txt`
