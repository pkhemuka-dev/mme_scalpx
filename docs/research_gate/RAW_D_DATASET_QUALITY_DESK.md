# RAW-D — Dataset Quality Desk

Date: 2026-05-01
Generated UTC: 2026-05-01T07:23:25.094442+00:00
Batch tag: batch_raw_d_dataset_quality_freeze_final_20260501_125325

## Purpose

Batch RAW-D creates the first useful RAW evidence desk: dataset quality.

It inspects availability and readiness of existing research_capture, replay, proof, live-capture, and RAW surfaces.

## Strict boundaries

- No broker IO.
- No Redis live writes.
- No order sending.
- No strategy/risk/execution ownership.
- No production mutation.
- No PnL computation.
- No strategy ranking.
- No OI-wall impact computation.
- No live runtime wiring.

## Live and replay separation

RAW-D keeps live and replay quality separate.

Live evidence quality checks whether real runtime/capture surfaces exist and are trustworthy.

Replay evidence quality checks whether replay/backtest surfaces exist for later richer PnL and strategy analysis.

Live-vs-replay parity is reserved for later batches.

## New files

- app/mme_scalpx/research_gate/dataset_quality.py
- bin/raw_dataset_quality.py

## Generated run artifact

- run/research_gate/raw_d_dataset_quality_20260501_125325/manifest.json
- run/research_gate/raw_d_dataset_quality_20260501_125325/dataset_quality_report.json
- run/research_gate/raw_d_dataset_quality_20260501_125325/RAW_D_DATASET_QUALITY_SUMMARY.md

## Verdict

PASS if proof JSON validates and all safety boundaries remain false.
