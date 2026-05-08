# Batch 27E — Deterministic Reset, Run ID, and Replay Integrity

Date: 2026-05-01

## Verdict

```text
PASS_REPLAY_DETERMINISTIC_RESET_INTEGRITY
```

## Scope

Batch 27E adds deterministic replay reset, deterministic run-id/hash helpers, and replay integrity proof surfaces.

It does not implement live-mimic feature execution, strategy-family reuse, risk replay, execution replay, or report expansion.

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
app/mme_scalpx/replay/reset.py
etc/replay/integrity/replay_integrity_policy.yaml
bin/proof_replay_deterministic_repeatability.py
bin/proof_replay_integrity.py
```

## Files patched additively

```text
app/mme_scalpx/replay/contracts.py
app/mme_scalpx/replay/integrity.py
app/mme_scalpx/replay/clock.py
app/mme_scalpx/replay/artifacts.py
app/mme_scalpx/replay/runner.py
bin/replay_run.py
```

## Replay reset components frozen

```text
replay_clock
local_replay_transport
feature_state
strategy_state
risk_state
execution_shadow_state
misr_consumed_trap_event_registry
miso_consumed_burst_event_registry
cooldown_state
position_state
artifact_state
```

## Integrity checks frozen

```text
deterministic_run_id
dataset_hash_present
profile_hash_present
experiment_hash_present
selected_window_hash_present
code_hash_present
event_order_monotonic
reset_cleanliness
artifact_root_is_run_replay
config_root_is_etc_replay
no_broker_call
no_live_redis_write
no_runtime_promotion
```

## Proof artifacts

```text
run/proofs/proof_replay_deterministic_repeatability.json
run/proofs/proof_replay_integrity.json
run/proofs/proof_replay_deterministic_reset_integrity.json
run/proofs/proof_replay_deterministic_reset_integrity_latest.json
run/proofs/proof_replay_dataset_manifest.json
run/proofs/proof_replay_no_broker_call.json
run/proofs/proof_replay_no_live_redis_write.json
run/proofs/proof_replay_no_runtime_promotion.json
```

## Confirmed pass condition

```text
deterministic_reset_integrity_ok = true
deterministic_repeatability_ok = true
integrity_ok = true
same_input_same_run_id = true
changed_dataset_changes_run_id = true
reset_cleanliness_ok = true
dataset_contract_ok = true
replay_safety_firewall_ok = true
paper_armed_approved = false
live_trading_approved = false
production_doctrine_changed = false
```

## Meaning

Replay now has deterministic reset, run-id, and integrity contracts.

This still does not make replay a complete live-mimic workstation.

## Next batch

```text
Batch 27F — Isolated live-shape replay transport
```

27F should create/verify replay-only transport surfaces so replay can produce live-compatible shapes without touching live Redis.
