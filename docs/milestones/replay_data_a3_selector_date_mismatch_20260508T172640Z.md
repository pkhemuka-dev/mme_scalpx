# REPLAY-DATA-A3 — Selector Available-Date Mismatch Diagnosis

UTC: 2026-05-08T17:26:41.235292+00:00

## Result

- Overall verdict: `FAIL`
- FAIL findings: `1`
- UNCLEAR findings: `1`
- Target dataset exists: `True`
- R5 available dates: `['2026-04-29']`
- Dataset date mentions: `['2026-04-16', '2026-04-17', '2026-04-24', '2026-04-26', '2026-04-27', '2026-04-29', '2026-04-30', '2026-05-01', '2026-05-02', '2026-05-03', '2026-05-07', '2027-01-15']`
- Metadata available dates: `['2026-04-29']`
- Session export dates: `['2026-04-17', '2026-04-20', '2026-04-21']`

## Findings

1. `FAIL` — `selector_logic_or_input_mismatch` — R5 says available date exists in dataset metadata/text, but selector rejected same date. Likely selector reads a different field/path or normalizes dates differently.
2. `UNCLEAR` — `session_export_vs_materialized_dataset_date_divergence` — run/session_exports dates differ from R5 dataset available_dates. This may be valid if the materialized dataset came from another archive, but must be proven before smoke replay.

## Safety

- code_patched=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false

## Recommended next batches

- REPLAY-DATA-A4 targeted patch plan for selector/date source mismatch; audit-only or sandbox-first
- Do not run REPLAY-SMOKE-A1 until selector/date mismatch is resolved

## Proof

- `run/proofs/proof_replay_data_a3_selector_date_mismatch_20260508T172640Z.json`
