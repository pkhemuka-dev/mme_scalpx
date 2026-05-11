# LANE F F4 RISK_PRODUCER_SURFACE_AND_STRATEGY_TO_RISK_HANDOFF_AUDIT Runbook

Purpose:
Directly audit `risk.py`, `strategy.py`, `execution.py`, strategy-family files, replay files, and existing artifacts for strategy-to-risk handoff and risk producer surfaces.

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
- `run/proofs/proof_lane_f_f4_risk_producer_surface_and_strategy_to_risk_handoff_audit_20260510_215913.json`
- `run/proofs/proof_lane_f_f4_risk_producer_surface_and_strategy_to_risk_handoff_audit_latest.json`
- `run/proofs/manifest_lane_f_f4_risk_producer_surface_and_strategy_to_risk_handoff_audit_latest.json`
- `run/proofs/sha256_lane_f_f4_risk_producer_surface_and_strategy_to_risk_handoff_audit_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F4_RISK_PRODUCER_SURFACE_AND_STRATEGY_TO_RISK_HANDOFF_AUDIT.md`
- `docs/runbooks/LANE_F_F4_RISK_PRODUCER_SURFACE_AND_STRATEGY_TO_RISK_HANDOFF_AUDIT_RUNBOOK.md`
- `run/status/LANE_F_F4_RISK_PRODUCER_SURFACE_AND_STRATEGY_TO_RISK_HANDOFF_AUDIT.txt`

Next recommended batch:
`F5_RISK_HANDOFF_REPAIR_PLAN_NO_PATCH_NO_LIVE_START`
