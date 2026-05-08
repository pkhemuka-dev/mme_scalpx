# REPLAY-DATA-A9 — Quote Schema Transform

UTC: 2026-05-08T17:48:36.377409+00:00

## Result

- Overall verdict: `PASS`
- Selector plan OK: `True`
- Available dates: `['2026-04-17']`
- Selected dates: `['2026-04-17']`
- Written rows by file: `{'quote_ticks_mme_fut_stream': 25016, 'quote_ticks_mme_opt_stream': 25005}`
- Skipped rows by file: `{'quote_ticks_mme_fut_stream': 0, 'quote_ticks_mme_opt_stream': 0}`
- Engine ready: `False`

## Safety

- code_patched=false
- files_transformed=true
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- engine_execution_performed=false
- orders_sent=false
- real_live_data_mutated=false

## Recommended next batches

- REPLAY-DATA-A10 selector-only replay_run CLI dry probe using quote transformed files
- REPLAY-DATA-A11 reconstruct features_rows from quote feeds

## Proof

- `run/proofs/proof_replay_data_a9_quote_schema_transform_20260508T174832Z.json`
