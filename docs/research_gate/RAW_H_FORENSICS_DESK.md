# RAW-H — Blocker, Missed-Trade, and False-Entry Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:42:36.572472+00:00
Batch tag: batch_raw_h_forensics_freeze_final_20260501_131236

## Purpose

Batch RAW-H adds conservative forensics for blockers, missed trades, and false entries.

RAW-H scans existing replay, research_capture, proof, report, and data artifacts for explicit blocker/candidate/decision/outcome evidence.

## Strict boundaries

- No broker IO.
- No Redis live writes.
- No order sending.
- No strategy/risk/execution ownership.
- No production mutation.
- No paper/live enablement.
- No PnL computation.
- No strategy ranking.
- No OI-wall impact computation.
- No invented missed trades.
- No invented false entries.

## Current prerequisite diagnosis

RAW-E:
- pnl_verdict: PNL_REJECT_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- trade_count: 44
- net_pnl_after_costs: -1105.0

RAW-F:
- rank_verdict: RANK_INSUFFICIENT_FAMILY_LABELS
- research_verdict: INCONCLUSIVE_DATA_INSUFFICIENT
- warning_count: 2

RAW-G:
- oi_verdict: OI_IMPACT_RESEARCH_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- oi_context_record_count: 1145
- pnl_linked_count: 44

## Generated run artifact

- run/research_gate/raw_h_forensics_20260501_131236/manifest.json
- run/research_gate/raw_h_forensics_20260501_131236/blocker_chain_report.json
- run/research_gate/raw_h_forensics_20260501_131236/missed_trade_report.json
- run/research_gate/raw_h_forensics_20260501_131236/false_entry_report.json
- run/research_gate/raw_h_forensics_20260501_131236/blocker_matrix.csv
- run/research_gate/raw_h_forensics_20260501_131236/forensics_source_breakdown.csv
- run/research_gate/raw_h_forensics_20260501_131236/RAW_H_FORENSICS_SUMMARY.md

## Verdict

PASS if proof JSON validates and all safety boundaries remain false.
