# REPLAY-DATA-A10 — Selector-Only replay_run CLI Dry Probe

UTC: 2026-05-08T17:50:27.963248+00:00

## Result

- Overall verdict: `PASS`
- Selector plan OK: `True`
- Available dates: `['2026-04-17']`
- Selected dates: `['2026-04-17']`
- Selection fingerprint: `dd673dc244ef028b6d2f498296f4300f9ecd8cc90b75fbf0b254b39e8e7dc677`
- CLI help OK: `True`
- py_compile OK: `True`
- Engine execution performed: `False`

## Safety

- code_patched=false
- files_transformed=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- engine_execution_performed=false
- orders_sent=false
- real_live_data_mutated=false

## Recommended next batches

- REPLAY-DATA-A11 reconstruct features_rows from quote feeds
- Then REPLAY-DATA-A12 reconstruct strategy_decisions shadow output

## Proof

- `run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_20260508T175024Z.json`
