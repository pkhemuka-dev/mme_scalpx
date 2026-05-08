# Batch 27K — Replay Batch / Date-Range Runner and Artifact Materialization

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_BATCH_RUNNER_ARTIFACT_MATERIALIZATION
```

## R1 note

27K initial run passed batch-runner proof but failed artifact materialization because `no_live_ok=false`.

Root cause: one artifact, most likely `00_manifest.json`, had safety flags nested under `safety` but not exposed at top level. R1 added top-level replay safety flags to the manifest payload and reran artifact + aggregate proofs.

## Safety result

```text
paper_armed: NOT APPROVED
live trading: NOT APPROVED
execution arming: NOT CREATED
real order sent: NO
broker APIs executed: NO
live Redis writes executed: NO
services started: NO
production doctrine changed: NO
artifact root: run/replay/
```

## Files patched in R1

```text
app/mme_scalpx/replay/artifact_materializer.py
```

## Files created/refreshed by 27K

```text
app/mme_scalpx/replay/batch_runner.py
app/mme_scalpx/replay/artifact_materializer.py
etc/replay/schemas/replay_batch_runner_contract_v1.json
etc/replay/batches/replay_batch_profile_manifest_v1.json
bin/replay_batch.py
bin/proof_replay_batch_runner.py
bin/proof_replay_artifact_materialization.py
```

## Replay run scopes proven

```text
single_day
date_range
date_list
intraday_window
scenario_matrix
```

## Replay artifacts proven

```text
00_manifest.json
01_dataset_summary.json
02_scenario_summary.json
03_feature_summary.json
04_strategy_summary.json
05_risk_summary.json
06_execution_shadow_summary.json
07_reproducibility.json
08_batch_summary.json
```

## Proof artifacts

```text
run/proofs/proof_replay_batch_runner.json
run/proofs/proof_replay_artifact_materialization.json
run/proofs/proof_replay_batch_runner_artifact_materialization.json
run/proofs/proof_replay_batch_runner_artifact_materialization_latest.json
```

## Confirmed pass condition

```text
batch_runner_artifact_materialization_ok = true
batch_runner_ok = true
artifact_materialization_ok = true
single_day_ok = true
date_range_ok = true
date_list_ok = true
intraday_window_ok = true
scenario_matrix_ok = true
required_artifacts_ok = true
manifest_ok = true
dataset_summary_ok = true
scenario_summary_ok = true
feature_summary_ok = true
strategy_summary_ok = true
risk_summary_ok = true
execution_summary_ok = true
reproducibility_ok = true
replay_safety_firewall_ok = true
broker_call_reachable = false
live_redis_write_reachable = false
runtime_promotion_reachable = false
paper_armed_approved = false
live_trading_approved = false
real_order_sent = false
production_doctrine_changed = false
```

## Explicit not-proven boundary

```text
batch_runner_shape = PROVEN_BY_27K
artifact_materialization = PROVEN_BY_27K
reproducibility_hash = PROVEN_BY_27K
full_live_replay_parity = NOT_PROVEN_IN_27K
```

## Next batch

```text
Batch 27L — Replay report/export workstation
```
