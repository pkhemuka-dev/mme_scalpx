# LANE F F6 GUARDED_RISK_EXECUTION_EVIDENCE_SURFACE_PATCH Runbook

Purpose:
Guardedly add append-only evidence helper surfaces to risk.py and execution.py.

This package:
- backs up target files
- appends helper blocks only if markers are absent
- compiles touched files
- rolls back on compile failure

This package does not:
- start services
- stop services
- write Redis
- delete Redis keys
- call brokers
- send orders
- run replay
- run PnL/economics
- admit dataset for backtest
- change risk doctrine
- change thresholds
- change order routing

Outputs:
- `run/proofs/proof_lane_f_f6_guarded_risk_execution_evidence_surface_patch_20260510_220634.json`
- `run/proofs/proof_lane_f_f6_guarded_risk_execution_evidence_surface_patch_latest.json`
- `run/proofs/manifest_lane_f_f6_guarded_risk_execution_evidence_surface_patch_latest.json`
- `run/proofs/sha256_lane_f_f6_guarded_risk_execution_evidence_surface_patch_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F6_GUARDED_RISK_EXECUTION_EVIDENCE_SURFACE_PATCH.md`
- `docs/runbooks/LANE_F_F6_GUARDED_RISK_EXECUTION_EVIDENCE_SURFACE_PATCH_RUNBOOK.md`
- `run/status/LANE_F_F6_GUARDED_RISK_EXECUTION_EVIDENCE_SURFACE_PATCH.txt`

Next recommended batch:
`F7_STATIC_VALIDATE_EVIDENCE_SURFACE_PATCH_NO_SERVICE_START_NO_REPLAY`
