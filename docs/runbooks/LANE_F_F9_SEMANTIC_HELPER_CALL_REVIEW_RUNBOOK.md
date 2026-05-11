# LANE F F9 SEMANTIC_HELPER_CALL_REVIEW Runbook

Purpose:
Semantically review F8 `get` call findings and distinguish safe local dictionary reads from executable network/broker/Redis calls.

This package does not:
- patch source code
- start services
- stop services
- write Redis
- delete Redis keys
- call brokers
- send orders
- run replay
- run PnL/economics
- admit dataset for backtest

Outputs:
- `run/proofs/proof_lane_f_f9_semantic_helper_call_review_20260510_221200.json`
- `run/proofs/proof_lane_f_f9_semantic_helper_call_review_latest.json`
- `run/proofs/manifest_lane_f_f9_semantic_helper_call_review_latest.json`
- `run/proofs/sha256_lane_f_f9_semantic_helper_call_review_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F9_SEMANTIC_HELPER_CALL_REVIEW.md`
- `docs/runbooks/LANE_F_F9_SEMANTIC_HELPER_CALL_REVIEW_RUNBOOK.md`
- `run/status/LANE_F_F9_SEMANTIC_HELPER_CALL_REVIEW.txt`

Next recommended batch:
`F10_EVIDENCE_SURFACE_INTEGRATION_DECISION_BLUEPRINT_NO_PATCH_NO_SERVICE_START`
