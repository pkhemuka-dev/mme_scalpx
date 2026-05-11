# 26-O23-Q-A4-R5B — Focused Dry-Run Plan Forensic

Generated UTC: 2026-05-11T05:17:45.358006+00:00

## Final verdict

`BLOCKED_A4_R5B_DRY_RUN_PLAN_FORENSIC_HAS_HARD_BLOCKERS`

## Classification

`BLOCKED`

## Finding

A4-R5 blocker was proof-shape normalization: R5 looked for top-level future_scope_candidate, while R4 proof stores the future controlled-paper scope under required_future_controlled_paper_scope and/or prior_evidence.mist_call_scope. Safety and dry-run plan creation were clean.

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

[
  "A4_R5_NOT_ACCEPTED_AS_PLAN_CREATED_WITH_SHAPE_BLOCKER_ONLY"
]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_EXPLICIT_USER_APPROVED_ENABLEMENT_PLAN",
  "REAL_LIVE_STILL_BLOCKED",
  "A4_R5B_IS_FORENSIC_ONLY_NOT_ENABLEMENT",
  "A4_R5B_DID_NOT_START_RISK_OR_EXECUTION",
  "A4_R5B_DID_NOT_CALL_BROKER",
  "A4_R5B_DID_NOT_VALIDATE_ACTUAL_ORDER_CYCLE"
]

## Next recommended batch

26-O23-Q-A4-R5C manual artifact closure / no enablement

## Artifacts

- Proof: `run/proofs/proof_lane_a4_r5b_focused_dry_run_plan_forensic_20260511_104740.json`
- Latest proof: `run/proofs/proof_lane_a4_r5b_focused_dry_run_plan_forensic_latest.json`
- Audit: `run/audits/lane_a4_r5b_focused_dry_run_plan_forensic_20260511_104740.json`
- SHA256: `run/proofs/sha256_lane_a4_r5b_focused_dry_run_plan_forensic_20260511_104740.txt`
