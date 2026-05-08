# RAW-I — Replay / Backtest Verdict Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:45:50.329374+00:00
Batch tag: batch_raw_i_replay_verdict_freeze_final_20260501_131550

## Purpose

Batch RAW-I consolidates RAW-D/E/F/G/H evidence into one replay/backtest research verdict.

RAW-I does not execute the replay engine and does not replace `app/mme_scalpx/replay`.

It only reads prior RAW proof outputs and writes a compact verdict pack.

## Strict boundaries

- No broker IO.
- No Redis live writes.
- No order sending.
- No strategy/risk/execution ownership.
- No production mutation.
- No paper/live enablement.
- No replay engine mutation.
- No research_capture mutation.
- No strategy config mutation.

## Current evidence before RAW-I

RAW-D:
- dataset_verdict: DATASET_PASS
- data_quality_score: 1.0

RAW-E:
- pnl_verdict: PNL_REJECT_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- trade_count: 44
- net_pnl_after_costs: -1105.0

RAW-F:
- rank_verdict: RANK_INSUFFICIENT_FAMILY_LABELS
- research_verdict: INCONCLUSIVE_DATA_INSUFFICIENT
- unknown_family_ratio_in_sample: 1.0

RAW-G:
- oi_verdict: OI_IMPACT_RESEARCH_NEGATIVE
- research_verdict: REJECT_NEGATIVE_EXPECTANCY
- oi_context_record_count: 1145
- pnl_linked_count: 44

RAW-H:
- forensics_verdict: FORENSICS_CONTEXT_FOUND_NO_OUTCOME_LABELS
- research_verdict: RESEARCH_ONLY_FINDING
- unknown_outcome_rate: 1.0

## Generated run artifact

- run/research_gate/raw_i_replay_verdict_20260501_131550/manifest.json
- run/research_gate/raw_i_replay_verdict_20260501_131550/replay_backtest_verdict.json
- run/research_gate/raw_i_replay_verdict_20260501_131550/replay_evidence_scorecard.csv
- run/research_gate/raw_i_replay_verdict_20260501_131550/RAW_I_REPLAY_BACKTEST_VERDICT_SUMMARY.md

## Expected posture

Based on current RAW-E/F/G/H evidence, this verdict should be diagnostic and not promotion-ready unless later enriched replay artifacts change the evidence.
