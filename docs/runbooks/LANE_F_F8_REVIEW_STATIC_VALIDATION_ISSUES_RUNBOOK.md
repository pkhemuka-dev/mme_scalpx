# LANE F F8 REVIEW_STATIC_VALIDATION_ISSUES Runbook

Purpose:
Review F7 static validation issues by classifying `broker`/`redis` hits as executable code or comment/docstring-only text.

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
- `run/proofs/proof_lane_f_f8_review_static_validation_issues_20260510_220949.json`
- `run/proofs/proof_lane_f_f8_review_static_validation_issues_latest.json`
- `run/proofs/manifest_lane_f_f8_review_static_validation_issues_latest.json`
- `run/proofs/sha256_lane_f_f8_review_static_validation_issues_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F8_REVIEW_STATIC_VALIDATION_ISSUES.md`
- `docs/runbooks/LANE_F_F8_REVIEW_STATIC_VALIDATION_ISSUES_RUNBOOK.md`
- `run/status/LANE_F_F8_REVIEW_STATIC_VALIDATION_ISSUES.txt`

Next recommended batch:
`F9_GUARDED_HELPER_SANITIZATION_OR_ROLLBACK_PLAN_NO_SERVICE_START`
