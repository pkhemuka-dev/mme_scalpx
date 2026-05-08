# Milestone — Batch RAW-E PnL Analytics Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:31:54.610596+00:00
Batch tag: batch_raw_e_pnl_analytics_freeze_final_20260501_130154

## Achieved

- Created RAW PnL analytics desk.
- Added app/mme_scalpx/research_gate/pnl.py.
- Added CLI wrapper bin/raw_pnl_report.py.
- Updated etc/research_gate/pnl_policy.json.
- Inspected relevant producer/consumer surfaces from sanitized archive.
- Preserved research_capture and replay ownership.
- Generated PnL report bundle under run/research_gate/raw_e_pnl_analytics_20260501_130154.
- Proved no broker IO, Redis live write, order sending, risk override, execution override, or production mutation was added.

## New / updated files

- app/mme_scalpx/research_gate/pnl.py
- bin/raw_pnl_report.py
- etc/research_gate/pnl_policy.json
- docs/research_gate/RAW_E_PNL_ANALYTICS_DESK.md
- run/research_gate/raw_e_pnl_analytics_20260501_130154/manifest.json
- run/research_gate/raw_e_pnl_analytics_20260501_130154/pnl_report.json
- run/research_gate/raw_e_pnl_analytics_20260501_130154/RAW_E_PNL_SUMMARY.md
- run/proofs/proof_raw_e_pnl_analytics.json
- run/proofs/proof_raw_e_freeze_final.json

## PnL verdict

- pnl_verdict: PNL_REJECT_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- trade_count: 44
- net_pnl_after_costs: -1105.0
- scanned_file_count: 57

## Safety confirmation

- live_runtime_touched = false
- broker_io_added = false
- redis_live_writer_added = false
- order_sending_added = false
- risk_override_added = false
- execution_override_added = false
- production_config_mutation_added = false
- pnl_computation_added = true
- strategy_ranking_added = false
- oi_wall_computation_added = false

## Verdict

PASS

## Next recommended batch

Batch RAW-F — strategy ranking desk.

RAW-F should consume PnL report outputs and rank family/side/regime performance without mutating strategy/risk/execution or enabling paper/live.
