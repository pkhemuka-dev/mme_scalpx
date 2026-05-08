# REPLAY-DATA-A6 — Real Session Export Schema + Canonicalization Plan

UTC: 2026-05-08T17:36:23.677895+00:00

## Result

- Overall verdict: `PASS`
- FAIL findings: `0`
- UNCLEAR findings: `2`
- Session count: `3`
- Best date: `2026-04-17`
- Direct materialization possible: `False`
- Offline reconstruction possible: `True`
- Missing required stems: `['strategy_decisions', 'risk_outputs', 'execution_shadow']`
- Partial A4 patch present: `True`

## Best Direct Mapping

- `features_rows` -> `run/session_exports/2026-04-17/health_features.json`
- `ticks_mme_fut_stream` -> `run/session_exports/2026-04-17/ticks_mme_fut_stream.csv`
- `ticks_mme_opt_stream` -> `run/session_exports/2026-04-17/ticks_mme_opt_stream.csv`

## Findings

1. `UNCLEAR` — `direct_materialization` — No session export directly contains all required replay stems; offline reconstruction or adapter materialization is needed.
2. `UNCLEAR` — `partial_a4_patch_present` — Partial A4 replay_run.py patch is still present; keep/revert decision should be made after canonical materialization path is proven.

## Safety

- code_patched=false
- files_materialized=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- engine_execution_performed=false

## Recommended next batches

- REPLAY-DATA-A7 create sandbox-only canonical day dataset from session export ticks, preserving source files and adding manifest
- Then run selector-only plan probe against sandbox canonical root

## Proof

- `run/proofs/proof_replay_data_a6_real_session_export_schema_plan_20260508T173622Z.json`
