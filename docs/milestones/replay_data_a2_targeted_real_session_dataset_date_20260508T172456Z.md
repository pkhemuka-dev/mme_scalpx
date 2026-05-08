# REPLAY-DATA-A2 — Targeted Real Session + Dataset Date Audit

UTC: 2026-05-08T17:24:58.143684+00:00

## Result

- Overall verdict: `FAIL`
- FAIL findings: `1`
- UNCLEAR findings: `0`
- Real session dates: `['2026-04-17', '2026-04-20', '2026-04-21']`
- Target dataset present: `True`
- R5 selector error detected: `True`

## Safety

- code_patched=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false

## Recommended next batches

- REPLAY-DATA-A3 diagnose selector available-date mismatch in target dataset metadata

## Findings

1. `FAIL` — `selector_date_mismatch` — Prior guarded replay execution reported available_dates but selector rejected the same single_day; diagnose dataset metadata/date-source mismatch before replay smoke.

## Proof

- `run/proofs/proof_replay_data_a2_targeted_real_session_dataset_date_20260508T172456Z.json`
