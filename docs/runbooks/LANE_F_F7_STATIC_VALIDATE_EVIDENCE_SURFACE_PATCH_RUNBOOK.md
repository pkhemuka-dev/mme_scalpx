# LANE F F7 STATIC_VALIDATE_EVIDENCE_SURFACE_PATCH Runbook

Purpose:
Statically validate the F6 append-only evidence helper patch.

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
- integrate helpers into runtime pipeline

Outputs:
- `run/proofs/proof_lane_f_f7_static_validate_evidence_surface_patch_20260510_220832.json`
- `run/proofs/proof_lane_f_f7_static_validate_evidence_surface_patch_latest.json`
- `run/proofs/manifest_lane_f_f7_static_validate_evidence_surface_patch_latest.json`
- `run/proofs/sha256_lane_f_f7_static_validate_evidence_surface_patch_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F7_STATIC_VALIDATE_EVIDENCE_SURFACE_PATCH.md`
- `docs/runbooks/LANE_F_F7_STATIC_VALIDATE_EVIDENCE_SURFACE_PATCH_RUNBOOK.md`
- `run/status/LANE_F_F7_STATIC_VALIDATE_EVIDENCE_SURFACE_PATCH.txt`

Next recommended batch:
`F8_REVIEW_STATIC_VALIDATION_ISSUES_NO_SERVICE_START_NO_REPLAY`
