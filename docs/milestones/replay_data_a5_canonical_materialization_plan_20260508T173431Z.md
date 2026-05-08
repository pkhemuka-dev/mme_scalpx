# REPLAY-DATA-A5 — Canonical Dataset Materialization Plan Audit

UTC: 2026-05-08T17:34:32.386865+00:00

## Result

- Overall verdict: `FAIL`
- FAIL findings: `1`
- UNCLEAR findings: `1`
- Dataset root exists: `True`
- Dataset file count: `1242`
- Target date match count: `1154`
- Materialization possible: `False`
- Unmatched required: `['features_rows', 'strategy_decisions', 'risk_outputs']`
- Partial A4 patch present: `True`

## Required Mapping Paths

- `execution_shadow` -> `run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/execution_shadow_semantic_no_order_validator_29cz/01_execution_shadow_semantic_no_order_validator_package.json`

## Optional Mapping Paths

- `option_context` -> `run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/input_surfaces/selected_option_context.json`
- `provider_runtime` -> `run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/input_surfaces/provider_runtime.json`

## Findings

1. `UNCLEAR` — `partial_a4_patch_present` — bin/replay_run.py still contains the partial A4 resolve_dataset_root patch. It may be useful but remains unproven until canonical topology is fixed.
2. `FAIL` — `canonical_mapping` — Could not map all required replay stems for canonical day materialization.

## Safety

- code_patched=false
- files_materialized=false
- services_started=false
- broker_calls_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- engine_execution_performed=false

## Recommended next batches

- REPLAY-DATA-A6 targeted source-artifact mapping repair or re-export session data to canonical replay schema
- Do not run replay smoke yet

## Proof

- `run/proofs/proof_replay_data_a5_canonical_materialization_plan_20260508T173431Z.json`
