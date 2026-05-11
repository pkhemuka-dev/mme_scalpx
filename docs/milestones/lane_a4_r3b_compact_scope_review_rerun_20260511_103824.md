# 26-O23-Q-A4-R3B — Compact Scope Review Rerun After Disk Recovery

Generated UTC: 2026-05-11T05:09:36.763772+00:00

## Final verdict

`MATERIAL_PASS_A4_R3B_SCOPE_REVIEW_INPUT_FROZEN_CONTROLLED_PAPER_STILL_BLOCKED`

## Classification

`MATERIAL-PASS-BUT-BLOCKED`

## Scope review

- Reviewable scope count: 10
- Observed scope count: 10
- Top reviewable scopes: [
  {
    "family": "MIST",
    "side": "CALL",
    "evidence_count": 2646,
    "candidate_mentions": 1366,
    "blocker_mentions": 1606,
    "hold_or_no_trade_mentions": 966,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISO",
    "side": "CALL",
    "evidence_count": 2141,
    "candidate_mentions": 781,
    "blocker_mentions": 1421,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISO",
    "side": "PUT",
    "evidence_count": 1981,
    "candidate_mentions": 781,
    "blocker_mentions": 1421,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISB",
    "side": "CALL",
    "evidence_count": 1901,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISC",
    "side": "CALL",
    "evidence_count": 1901,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISR",
    "side": "CALL",
    "evidence_count": 1901,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MIST",
    "side": "PUT",
    "evidence_count": 1741,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISB",
    "side": "PUT",
    "evidence_count": 1741,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISC",
    "side": "PUT",
    "evidence_count": 1741,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  },
  {
    "family": "MISR",
    "side": "PUT",
    "evidence_count": 1741,
    "candidate_mentions": 781,
    "blocker_mentions": 1261,
    "hold_or_no_trade_mentions": 621,
    "review_input_quality": "REVIEWABLE",
    "controlled_paper_approval": false
  }
]

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
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_SEPARATE_SCOPE_SELECTION_AND_GOVERNANCE_REVIEW",
  "REAL_LIVE_STILL_BLOCKED",
  "A4_R3B_DOES_NOT_APPROVE_PAPER",
  "A4_R3B_DOES_NOT_ENABLE_BROKER_ORDERS",
  "A4_R3B_DOES_NOT_START_RISK_OR_EXECUTION",
  "PRODUCER_ONLY_OBSERVATION_FIELD_IS_REVIEW_INPUT_ONLY_NOT_APPROVAL"
]

## Next recommended batch

26-O23-Q-A4-R4 controlled-paper gate checklist audit only / no enablement

## Artifacts

- Proof: `run/proofs/proof_lane_a4_r3b_compact_scope_review_rerun_20260511_103824.json`
- Latest proof: `run/proofs/proof_lane_a4_r3b_compact_scope_review_rerun_latest.json`
- Scope matrix: `run/audits/lane_a4_r3b_compact_scope_review_rerun_20260511_103824_scope_matrix.json`
- SHA256: `run/proofs/sha256_lane_a4_r3b_compact_scope_review_rerun_20260511_103824.txt`
