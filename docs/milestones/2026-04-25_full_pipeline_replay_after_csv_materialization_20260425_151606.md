# Full Pipeline Replay After CSV Materialization — 2026-04-25

## Purpose
Verify downstream replay stages after enabling CSV feed event materialization.

## Dataset
- run/replay_datasets/session_exports_quote_compat_20260425_150651/2026-04-21

## Scopes
- feeds_features
- feeds_features_strategy
- feeds_features_strategy_risk
- feeds_features_strategy_risk_execution_shadow

## Artifacts
- run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/full_pipeline_stage_summary.json
- run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606

## Key prior proof
- feeds_only injected 50,021 feed events from CSV.
