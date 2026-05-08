# REPLAY-DATA-A7 — Sandbox Canonical Day Dataset Materialization

UTC: 2026-05-08T17:37:41.186294+00:00

## Result

- Overall verdict: `FAIL`
- FAIL findings: `2`
- UNCLEAR findings: `1`
- Selector plan OK: `False`
- Available dates: `[]`
- Selected dates: `[]`
- Engine ready: `False`
- Canonical root: `run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z`

## Findings

1. `FAIL` — `selector_probe` — Selector could not build a plan for canonical raw tick candidate
2. `FAIL` — `selector_probe` — Selector plan did not select source date
3. `UNCLEAR` — `engine_readiness` — Canonical candidate is selector-ready/raw-tick-only, not engine-ready until features/strategy/risk/execution surfaces are reconstructed.

## Safety

- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- engine_execution_performed=false
- orders_sent=false
- real_live_data_mutated=false

## Recommended next batches

- REPLAY-DATA-A8 schema-map raw ticks/health_features into features_rows reconstruction candidate
- Do not run full replay engine until features_rows, strategy_decisions, risk_outputs, and execution_shadow are reconstructed or consciously stubbed for a selector-only test.

## Proof

- `run/proofs/proof_replay_data_a7_sandbox_canonical_day_dataset_20260508T173739Z.json`
