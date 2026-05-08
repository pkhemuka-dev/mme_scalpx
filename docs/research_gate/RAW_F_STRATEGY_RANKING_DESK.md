# RAW-F — Strategy Ranking Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:35:42.507550+00:00
Batch tag: batch_raw_f_strategy_ranking_freeze_final_20260501_130542

## Purpose

Batch RAW-F adds strategy ranking for RAW / Research Gate.

RAW-F consumes RAW-E PnL report output and ranks available buckets by family, side, regime, provider mode, family-side matrix, and source artifact breakdown.

## Strict boundaries

- No broker IO.
- No Redis live writes.
- No order sending.
- No strategy/risk/execution ownership.
- No production mutation.
- No PnL recomputation from broker/live state.
- No OI-wall impact computation.
- No paper/live enablement.
- No strategy config mutation.

## Important caution

RAW-E result was:

- pnl_verdict: PNL_REJECT_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- trade_count: 44
- net_pnl_after_costs: -1105.0

If overall PnL is negative, RAW-F rankings are diagnostic only.

## Generated run artifact

- run/research_gate/raw_f_strategy_ranking_20260501_130542/manifest.json
- run/research_gate/raw_f_strategy_ranking_20260501_130542/strategy_rank_report.json
- run/research_gate/raw_f_strategy_ranking_20260501_130542/family_side_matrix.csv
- run/research_gate/raw_f_strategy_ranking_20260501_130542/source_artifact_breakdown.csv
- run/research_gate/raw_f_strategy_ranking_20260501_130542/RAW_F_STRATEGY_RANK_SUMMARY.md

## Verdict

PASS if proof JSON validates and all safety boundaries remain false.
