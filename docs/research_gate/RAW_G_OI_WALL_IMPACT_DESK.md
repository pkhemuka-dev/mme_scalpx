# RAW-G — OI-Wall Impact Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:38:54.122409+00:00
Batch tag: batch_raw_g_oi_wall_impact_freeze_final_20260501_130854

## Purpose

Batch RAW-G adds OI-wall / strike-selection impact evidence for RAW / Research Gate.

RAW-G scans existing replay, research_capture, proof, report, and data artifacts for OI/OI-wall/strike-score context and optional PnL linkage.

## Strict boundaries

- No broker IO.
- No Redis live writes.
- No order sending.
- No strategy/risk/execution ownership.
- No production mutation.
- No paper/live enablement.
- No PnL recomputation from broker/live state.
- No strategy ranking.
- OI wall is not immediate trigger truth.

## OI-wall law

OI wall is research, context, strike-quality, and slow-evidence surface.

RAW-G must never turn OI wall into a direct entry trigger.

## Current prerequisites

RAW-E:
- pnl_verdict: PNL_REJECT_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- trade_count: 44
- net_pnl_after_costs: -1105.0

RAW-F:
- rank_verdict: RANK_INSUFFICIENT_FAMILY_LABELS
- research_verdict: INCONCLUSIVE_DATA_INSUFFICIENT
- warning_count: 2

## Generated run artifact

- run/research_gate/raw_g_oi_wall_impact_20260501_130854/manifest.json
- run/research_gate/raw_g_oi_wall_impact_20260501_130854/oi_wall_impact_report.json
- run/research_gate/raw_g_oi_wall_impact_20260501_130854/oi_wall_context_matrix.csv
- run/research_gate/raw_g_oi_wall_impact_20260501_130854/oi_wall_source_breakdown.csv
- run/research_gate/raw_g_oi_wall_impact_20260501_130854/RAW_G_OI_WALL_SUMMARY.md

## Verdict

PASS if proof JSON validates and all safety boundaries remain false.
