# Batch 27F — Isolated Live-Shape Replay Transport

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_ISOLATED_LIVE_SHAPE_TRANSPORT
```

## Scope

Batch 27F creates replay-only transport surfaces so replay can produce live-compatible event/state shapes without touching live Redis.

It does not implement live feature-family execution, strategy-family reuse, risk replay, execution replay, or report expansion.

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
app/mme_scalpx/replay/transport.py
app/mme_scalpx/replay/live_adapter.py
etc/replay/schemas/replay_live_shape_transport_contract_v1.json
bin/proof_replay_contract_surface.py
bin/proof_replay_live_shape_transport.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/injector.py
app/mme_scalpx/replay/engine.py
bin/replay_run.py
```

## Replay live-shape surfaces frozen

```text
futures_tick
selected_option_tick
dhan_context
oi_ladder
provider_runtime
feature_payload
strategy_decision
risk_shadow
execution_shadow
```

## Proof artifacts

```text
run/proofs/proof_replay_contract_surface.json
run/proofs/proof_replay_live_shape_transport.json
run/proofs/proof_replay_isolated_live_shape_transport.json
run/proofs/proof_replay_isolated_live_shape_transport_latest.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
run/proofs/proof_replay_dataset_manifest.json
run/proofs/proof_replay_deterministic_repeatability.json
run/proofs/proof_replay_integrity.json
```

## Confirmed pass condition

```text
isolated_live_shape_transport_ok = true
contract_surface_ok = true
live_shape_transport_ok = true
namespace_ok = true
event_count_ok = true
state_count_ok = true
reset_ok = true
dataset_contract_ok = true
deterministic_reset_integrity_ok = true
replay_safety_firewall_ok = true
broker_call_reachable = false
live_redis_write_reachable = false
runtime_promotion_reachable = false
paper_armed_approved = false
live_trading_approved = false
production_doctrine_changed = false
```

## Meaning

Replay now has isolated in-memory live-shape transport infrastructure.

This still does not make replay a complete live-mimic workstation. It only provides the safe transport seam needed for later feature-family and strategy-family replay adapters.

## Next batch

```text
Batch 27G — Feature-family replay adapter
```

27G should reuse live feature-family builders through replay-only transport/state surfaces, while preserving 27C safety and not touching live Redis.
