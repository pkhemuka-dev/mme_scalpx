# Batch 27D — Replay Dataset Contract Expansion

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_DATASET_CONTRACT_EXPANSION
```

## Scope

Batch 27D freezes replay input/data contract surfaces only.

It does not implement live-mimic execution, feature-family reuse, strategy-family reuse, risk replay, or reporting expansion.

## Safety result

```text
paper_armed: NOT APPROVED
live trading: NOT APPROVED
execution arming: NOT CREATED
broker APIs executed: NO
live Redis writes executed: NO
services started: NO
production doctrine changed: NO
```

## Files created / refreshed

```text
etc/replay/datasets/replay_live_surface_contract_v2.json
etc/replay/datasets/replay_dhan_context_contract_v1.json
etc/replay/datasets/replay_oi_ladder_contract_v1.json
etc/replay/datasets/replay_provider_runtime_contract_v1.json
etc/replay/datasets/replay_dataset_contract_manifest_v1.json
bin/proof_replay_dataset_manifest.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/dataset.py
```

## Files inspected but not patched

```text
app/mme_scalpx/replay/frame_export.py
app/mme_scalpx/main.py
app/mme_scalpx/core/names.py
app/mme_scalpx/core/models.py
app/mme_scalpx/core/settings.py
app/mme_scalpx/core/redisx.py
app/mme_scalpx/core/codec.py
app/mme_scalpx/core/clock.py
app/mme_scalpx/services/feeds.py
app/mme_scalpx/services/features.py
app/mme_scalpx/services/strategy.py
app/mme_scalpx/services/risk.py
app/mme_scalpx/services/execution.py
app/mme_scalpx/services/feature_family/
app/mme_scalpx/services/strategy_family/
etc/replay/
etc/strategy_family/
etc/brokers/
```

## Frozen replay dataset surfaces

```text
futures
selected_option
Dhan context
OI ladder / OI wall
provider runtime
CALL/PUT separation
MISO readiness
```

## Proof artifacts

```text
run/proofs/proof_replay_dataset_manifest.json
run/proofs/proof_replay_dataset_contract_expansion_latest.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
```

## Confirmed pass condition

```text
dataset_contract_ok = true
futures_surface_ok = true
selected_option_surface_ok = true
dhan_context_surface_ok = true
oi_ladder_surface_ok = true
provider_runtime_surface_ok = true
call_put_separation_surface_ok = true
miso_readiness_surface_ok = true
paper_armed_approved = false
live_trading_approved = false
production_doctrine_changed = false
```

## Meaning

Replay now has frozen dataset/input contracts for live-mimic development.

This still does not make replay a complete live-mimic workstation.

## Next batch

```text
Batch 27E — Deterministic reset, run ID, and replay integrity
```

27E should add deterministic reset and reproducibility checks for:

```text
replay clock
local replay transport
feature state
strategy state
risk state
execution-shadow state
MISR consumed trap_event_id registry
MISO consumed burst_event_id registry
cooldown state
position state
artifact state
dataset/profile/code hash
```
