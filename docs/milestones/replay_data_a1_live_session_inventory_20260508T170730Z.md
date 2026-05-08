# REPLAY-DATA-A1 — Recorded Live-Session Inventory Audit

UTC: 2026-05-08T17:11:38.680081+00:00

## Result

- Overall verdict: `PASS`
- Inventory pass: `True`
- Candidate files: `91972`
- Candidate sessions: `858`
- Best candidate: `batch_raw_i_replay_verdict_freeze_final_20260501_131550_inspection`
- Best candidate readiness: `HIGH`
- Best candidate score: `162`

## Best Candidate Missing Surfaces

- None detected by inventory scoring.

## Safety

- code_patched=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false

## Recommended next batches

- REPLAY-CAP-A1 replay module capability audit
- REPLAY-SMOKE-A1 run dry replay smoke on best candidate if materialization path exists

## Proof

- `run/proofs/proof_replay_data_a1_live_session_inventory_20260508T170730Z.json`
