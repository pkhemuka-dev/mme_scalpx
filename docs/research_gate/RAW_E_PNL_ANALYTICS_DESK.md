# RAW-E — PnL Analytics Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:31:54.610596+00:00
Batch tag: batch_raw_e_pnl_analytics_freeze_final_20260501_130154

## Purpose

Batch RAW-E adds PnL analytics for RAW / Research Gate.

RAW-E calculates PnL only from existing replay, research_capture, proof, report, or data artifacts that contain explicit PnL fields or entry/exit/quantity fields.

## Strict boundaries

- No broker IO.
- No Redis live writes.
- No order sending.
- No strategy/risk/execution ownership.
- No production mutation.
- No strategy ranking.
- No OI-wall impact computation.
- No live runtime wiring.
- No invented trades.

## What RAW-E may calculate

- gross_pnl
- net_pnl_after_costs
- trade_count
- winning_trades
- losing_trades
- win_rate
- profit_factor
- expectancy
- max_drawdown
- PnL by family
- PnL by side
- PnL by regime
- PnL by provider mode

## What RAW-E must not decide

RAW-E must not decide best strategy. That is RAW-F.

RAW-E must not decide OI-wall usefulness. That is RAW-G.

RAW-E must not approve paper/live. That remains promotion firewall work.

## Generated run artifact

- run/research_gate/raw_e_pnl_analytics_20260501_130154/manifest.json
- run/research_gate/raw_e_pnl_analytics_20260501_130154/pnl_report.json
- run/research_gate/raw_e_pnl_analytics_20260501_130154/RAW_E_PNL_SUMMARY.md

## Verdict

PASS if proof JSON validates and all safety boundaries remain false.
