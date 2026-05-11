# 26-O23-Q-A4-R2D — Targeted Proof-Shape Forensic

Generated UTC: 2026-05-11T04:46:25.086384+00:00

## Final verdict

`MATERIAL_PASS_A4_R2D_PROOF_SHAPE_CLEARED_CONTROLLED_PAPER_STILL_BLOCKED_PENDING_SCOPE_REVIEW`

## Classification

`MATERIAL-PASS-BUT-BLOCKED`

## Findings

- A4-R1 link validated: True
- A4-R2 shape blocker cleared: True
- Fresh safety clean: True
- Fresh streams present: True

## Root cause

A4-R2 contained material live/safety readiness evidence, but its hard_blockers retained A4_R1_latest_proof_missing_or_not_material_pass from the earlier strict validator. A4-R1 is now validated by later proof-chain inspection. This is a proof-shape/validator artifact, not a live readiness or order-safety failure.

## Safety

- source_patch_applied: false
- service_start_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_attempted: false
- broker_calls_executed: false
- live_redis_writes_executed: false
- orders_zero: True
- position_flat: True
- no_risk_execution_pids: True
- no_paper_live_broker_env_enabled: True

## Hard blockers

[]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_SEPARATE_EVIDENCE_BACKED_SCOPE_REVIEW",
  "REAL_LIVE_STILL_BLOCKED",
  "A4_R2D_DOES_NOT_APPROVE_PAPER",
  "A4_R2D_DOES_NOT_TEST_BROKER_ORDERS",
  "PRODUCER_ONLY_OBSERVATION_FIELD_IS_NOT_APPROVAL"
]

## Next recommended batch

26-O23-Q-A4-R3 evidence-backed controlled-paper scope review audit only / no enablement

## Artifacts

- Proof: `run/proofs/proof_lane_a4_r2d_targeted_proof_shape_forensic_20260511_101619.json`
- Latest proof: `run/proofs/proof_lane_a4_r2d_targeted_proof_shape_forensic_latest.json`
- Audit: `run/audits/lane_a4_r2d_targeted_proof_shape_forensic_20260511_101619.json`
- SHA256: `run/proofs/sha256_lane_a4_r2d_targeted_proof_shape_forensic_20260511_101619.txt`
