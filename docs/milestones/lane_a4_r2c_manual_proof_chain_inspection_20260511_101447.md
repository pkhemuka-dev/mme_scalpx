# 26-O23-Q-A4-R2C — Manual Proof-Chain Inspection

Generated UTC: 2026-05-11T04:44:53.430048+00:00

## Final verdict

`BLOCKED_A4_R2C_MANUAL_PROOF_CHAIN_HAS_HARD_BLOCKERS`

## Classification

`BLOCKED`

## Manual chain findings

- A4-R1 link validated now: True
- A4-R2 material-pass except R1 link now: False
- A4-R2B confirmed R1 link validated: False
- A4-R2B blocker explained: True
- Fresh safety clean: True
- Fresh streams current: True

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
  "A4_R2_NOT_MATERIAL_PASS_EXCEPT_R1_LINK_BY_MANUAL_NORMALIZER"
]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_SEPARATE_EVIDENCE_BACKED_SCOPE_REVIEW",
  "REAL_LIVE_STILL_BLOCKED",
  "A4_R2C_DOES_NOT_APPROVE_PAPER",
  "A4_R2C_DOES_NOT_TEST_BROKER_ORDERS",
  "PRODUCER_ONLY_OBSERVATION_FIELD_IS_NOT_APPROVAL"
]

## Next recommended batch

26-O23-Q-A4-R2D targeted proof-shape forensic / no paper enablement

## Artifacts

- Proof: `run/proofs/proof_lane_a4_r2c_manual_proof_chain_inspection_20260511_101447.json`
- Latest proof: `run/proofs/proof_lane_a4_r2c_manual_proof_chain_inspection_latest.json`
- Audit: `run/audits/lane_a4_r2c_manual_proof_chain_inspection_20260511_101447.json`
- SHA256: `run/proofs/sha256_lane_a4_r2c_manual_proof_chain_inspection_20260511_101447.txt`
