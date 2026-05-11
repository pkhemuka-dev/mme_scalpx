# LANE F F3 STRATEGY_RISK_BLOCKER_DIAGNOSTIC_BLUEPRINT Runbook

Purpose:
Create a no-mutation diagnostic blueprint for why existing rows are `NO_TRADE` / `risk_blocked`.

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
- `run/proofs/proof_lane_f_f3_strategy_risk_blocker_diagnostic_blueprint_20260510_215328.json`
- `run/proofs/proof_lane_f_f3_strategy_risk_blocker_diagnostic_blueprint_latest.json`
- `run/proofs/manifest_lane_f_f3_strategy_risk_blocker_diagnostic_blueprint_latest.json`
- `run/proofs/sha256_lane_f_f3_strategy_risk_blocker_diagnostic_blueprint_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F3_STRATEGY_RISK_BLOCKER_DIAGNOSTIC_BLUEPRINT.md`
- `docs/runbooks/LANE_F_F3_STRATEGY_RISK_BLOCKER_DIAGNOSTIC_BLUEPRINT_RUNBOOK.md`
- `run/status/LANE_F_F3_STRATEGY_RISK_BLOCKER_DIAGNOSTIC_BLUEPRINT.txt`

Next recommended batch:
`F4_RISK_PRODUCER_SURFACE_AND_STRATEGY_TO_RISK_HANDOFF_AUDIT_NO_PATCH_NO_LIVE_START`
