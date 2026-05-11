# LANE F F5 RISK_HANDOFF_REPAIR_PLAN_NO_PATCH Runbook

Purpose:
Classify F4 handoff gaps into real source-surface gaps vs naming drift and create a repair plan.

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
- `run/proofs/proof_lane_f_f5_risk_handoff_repair_plan_no_patch_20260510_220244.json`
- `run/proofs/proof_lane_f_f5_risk_handoff_repair_plan_no_patch_latest.json`
- `run/proofs/manifest_lane_f_f5_risk_handoff_repair_plan_no_patch_latest.json`
- `run/proofs/sha256_lane_f_f5_risk_handoff_repair_plan_no_patch_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F5_RISK_HANDOFF_REPAIR_PLAN_NO_PATCH.md`
- `docs/runbooks/LANE_F_F5_RISK_HANDOFF_REPAIR_PLAN_NO_PATCH_RUNBOOK.md`
- `run/status/LANE_F_F5_RISK_HANDOFF_REPAIR_PLAN_NO_PATCH.txt`

Next recommended batch:
`F6_GUARDED_RISK_EXECUTION_EVIDENCE_SURFACE_PATCH_NO_SERVICE_START_NO_REPLAY`
