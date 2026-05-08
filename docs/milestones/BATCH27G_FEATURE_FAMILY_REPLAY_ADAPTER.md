# Batch 27G — Feature-Family Replay Adapter

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_FEATURE_FAMILY_ADAPTER
```

## Scope

Batch 27G creates replay-only feature-family adapter surfaces and proves the replay feature payload shape.

It does not execute strategy-family decisions.
It does not approve paper/live.
It does not prove full live feature-computation parity.
It proves replay-safe feature payload shape for all five families and both sides.

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
app/mme_scalpx/replay/feature_adapter.py
etc/replay/schemas/replay_feature_family_adapter_contract_v1.json
bin/proof_replay_feature_family_parity.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/engine.py
bin/replay_run.py
```

## Replay feature families covered

```text
MIST CALL
MIST PUT
MISB CALL
MISB PUT
MISC CALL
MISC PUT
MISR CALL
MISR PUT
MISO CALL
MISO PUT
```

## Replay feature payload surfaces proven

```text
family_features_json
family_surfaces_json
family_frames_json
CALL/PUT side separation
MIST surface terms
MISB surface terms
MISC surface terms
MISR surface terms
MISO surface terms
MISO provider_ready_miso
MISO Dhan context freshness
MISO OI context / OI wall context
```

## Proof artifacts

```text
run/proofs/proof_replay_feature_family_parity.json
run/proofs/proof_replay_feature_family_adapter.json
run/proofs/proof_replay_feature_family_adapter_latest.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
run/proofs/proof_replay_dataset_manifest.json
run/proofs/proof_replay_deterministic_repeatability.json
run/proofs/proof_replay_integrity.json
run/proofs/proof_replay_contract_surface.json
run/proofs/proof_replay_live_shape_transport.json
```

## Confirmed pass condition

```text
feature_family_adapter_ok = true
family_features_json_present = true
family_surfaces_json_present = true
family_frames_json_present = true
call_put_side_separation_ok = true
all_5_family_surfaces_present = true
miso_provider_ready_replayable = true
miso_dhan_context_replayable = true
miso_oi_context_replayable = true
no_strategy_decision_ok = true
isolated_live_shape_transport_ok = true
replay_safety_firewall_ok = true
broker_call_reachable = false
live_redis_write_reachable = false
runtime_promotion_reachable = false
paper_armed_approved = false
live_trading_approved = false
production_doctrine_changed = false
```

## Explicit not-proven boundary

```text
full_live_feature_computation_parity = NOT_PROVEN_IN_27G
strategy_family_decision_parity = NOT_PROVEN_IN_27G
safe_payload_shape_parity = PROVEN_BY_27G
```

## Meaning

Replay now has a safe replay-only feature-family payload adapter and proof for all five families.

This is still not a complete live-mimic workstation because live feature-builder execution and strategy-family decision replay are not yet proven.

## Next batch

```text
Batch 27H — Strategy-family replay adapter and arbitration
```

27H should add strategy-family replay adapter and arbitration proof while preserving no paper/live and no broker/no live Redis guarantees.
