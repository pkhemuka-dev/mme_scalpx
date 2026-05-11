# LANE F F11 GUARDED_EVIDENCE_HELPER_INTEGRATION_PATCH Runbook

Purpose:
Guardedly integrate safe Lane F evidence helper surfaces into runtime payload-return seams as nested metadata only.

This package:
- requires F9 PASS and F10 PASS
- backs up risk.py and execution.py before mutation
- patches only if both files have safe candidate seams
- compiles after patch
- rolls back on compile failure
- uses nested setdefault metadata only

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
- change position truth

Outputs:
- `run/proofs/proof_lane_f_f11_guarded_evidence_helper_integration_patch_20260510_222226.json`
- `run/proofs/proof_lane_f_f11_guarded_evidence_helper_integration_patch_latest.json`
- `run/proofs/manifest_lane_f_f11_guarded_evidence_helper_integration_patch_latest.json`
- `run/proofs/sha256_lane_f_f11_guarded_evidence_helper_integration_patch_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F11_GUARDED_EVIDENCE_HELPER_INTEGRATION_PATCH.md`
- `docs/runbooks/LANE_F_F11_GUARDED_EVIDENCE_HELPER_INTEGRATION_PATCH_RUNBOOK.md`
- `run/status/LANE_F_F11_GUARDED_EVIDENCE_HELPER_INTEGRATION_PATCH.txt`
- backup dir: `run/_code_backups/lane_f_f11_guarded_evidence_helper_integration_patch_20260510_222226`

Next recommended batch:
`F12_REVIEW_F11_PATCH_GUARD_STOP_NO_SERVICE_START`
