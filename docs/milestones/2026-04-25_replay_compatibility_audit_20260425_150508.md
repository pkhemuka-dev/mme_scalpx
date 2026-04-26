# Replay Compatibility Audit — 2026-04-25

## Purpose
Closed-market replay compatibility audit using recorded live session export data.

## Dataset
- run/session_exports/2026-04-21/ticks_mme_fut_stream.csv
- run/session_exports/2026-04-21/ticks_mme_opt_stream.csv

## Scopes attempted
- feeds_only
- feeds_features
- feeds_features_strategy
- feeds_features_strategy_risk
- feeds_features_strategy_risk_execution_shadow

## Artifacts
- run/proofs/replay_compatibility_audit_20260425_150508/replay_compatibility_plan.json
- run/proofs/replay_compatibility_audit_20260425_150508/schema_recheck.log
- run/proofs/replay_compatibility_audit_20260425_150508/replay_compatibility_summary.json
- run/proofs/replay_compatibility_audit_20260425_150508/run_artifact_inventory.txt
- run/replay_audits/20260425_150508

## Safety
- live orders disabled
- paper armed blocked
- replay channel prefix: replay:audit:20260425_150508
