# 26-O23-Q-A4-R2 — Readiness Report + Blocker Matrix

Generated UTC: 2026-05-11T04:40:53.798032+00:00

## Final verdict

`BLOCKED_A4_R2_READINESS_REPORT_HAS_HARD_BLOCKERS`

## Classification

`MATERIAL-PASS-BUT-BLOCKED`

A4-R2 freezes readiness evidence only. It does not approve controlled paper.

## Live readiness

- market_session_window_ok: True
- features_live_now: True
- decisions_live_now: True
- family_scope_candidates_json: True
- payload_json: True
- activation_report_json: True
- families_appearing: ['MIST', 'MISB', 'MISC', 'MISR', 'MISO']
- owner_scope_candidate_count: 11770
- evidence_backed_candidate_count_conservative: 11770

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
  "A4_R1_latest_proof_missing_or_not_material_pass"
]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_SEPARATE_EVIDENCE_BACKED_SCOPE_REVIEW",
  "REAL_LIVE_STILL_BLOCKED",
  "A4_R2_DOES_NOT_APPROVE_PAPER",
  "A4_R2_DOES_NOT_TEST_BROKER_ORDERS",
  "PRODUCER_ONLY_OBSERVATION_FIELD_IS_NOT_APPROVAL"
]

## Next recommended batch

26-O23-Q-A4-R2B focused blocker audit / no paper enablement

## Artifacts

- Proof: `run/proofs/proof_lane_a4_r2_readiness_report_blocker_matrix_20260511_100943.json`
- Latest proof: `run/proofs/proof_lane_a4_r2_readiness_report_blocker_matrix_latest.json`
- Matrix: `run/audits/lane_a4_r2_readiness_report_blocker_matrix_20260511_100943.json`
- SHA256: `run/proofs/sha256_lane_a4_r2_readiness_report_blocker_matrix_20260511_100943.txt`
