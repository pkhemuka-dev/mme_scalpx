# REPLAY-DATA-A4B — Failed A4 Reconciliation + Dataset Topology Audit

UTC: 2026-05-08T17:32:45.952072+00:00

## Result

- Overall verdict: `FAIL`
- FAIL findings: `3`
- UNCLEAR findings: `1`
- Dataset root exists: `True`
- Day dir count: `0`
- Day dirs: `[]`
- Selector plan OK: `False`
- Selector captured available dates: `[]`
- Partial A4 patch present: `True`

## Findings

1. `UNCLEAR` — `partial_a4_patch_present` — A4 modified bin/replay_run.py but failed before proof creation; patch must be reconciled before further replay smoke.
2. `FAIL` — `dataset_day_topology` — Resolved dataset root contains no YYYY-MM-DD day directories discoverable by filesystem scan.
3. `FAIL` — `repository_discovery` — Selector receives available_dates that do not include 2026-04-29 even after root resolution.
4. `FAIL` — `selector_plan` — Selector still cannot build single_day plan for 2026-04-29.

## Safety

- code_patched=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- engine_execution_performed=false

## Recommended next batches

- REPLAY-DATA-A5 patch dataset discovery/date source OR materialize canonical YYYY-MM-DD day dataset; choose based on A4B topology evidence
- Do not run REPLAY-SMOKE-A1 yet

## Proof

- `run/proofs/proof_replay_data_a4b_failed_patch_reconcile_dataset_topology_20260508T173239Z.json`
