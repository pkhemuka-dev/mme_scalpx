# Replay Run CSV Materialization Inspect — 2026-04-25

## Purpose
Inspect why replay_run accepts CSV dataset but feed stage injects zero rows.

## Current known gap
- Dataset selected
- CSV rows exist
- Feed stage total_injected=0
- Features/strategy/risk outputs are empty

## Artifacts
- run/proofs/replay_run_csv_materialization_inspect_20260425_151146/replay_run_materialization_extract.log
- run/proofs/replay_run_csv_materialization_inspect_20260425_151146/dataset_reader_extract.log

## Expected next
Patch replay_run CSV materialization or timestamp conversion if confirmed.
