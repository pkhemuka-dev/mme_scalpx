# Batch 26F — MISR Trap-Zone + Trap-Event Lifecycle Repair

Date: 2026-04-27  
Timestamp: 20260427_001200

## Verdict

Batch 26F patch package executed.

Expected proof:

- `run/proofs/batch26f_misr_trap_event_lifecycle_repair.json`
- `batch26f_misr_trap_event_lifecycle_repair_ok=true`

## Files patched / created

Patched:

- `app/mme_scalpx/services/feature_family/misr_surface.py`
- `app/mme_scalpx/services/features.py`
- `app/mme_scalpx/services/strategy_family/misr.py`

Created:

- `app/mme_scalpx/services/feature_family/misr_zones.py`
- `app/mme_scalpx/services/strategy_family/event_registry.py`

## Contract repaired

MISR trap-zone repair:

- deterministic ORB_HIGH zone generation from explicit ORB high source fields
- deterministic ORB_LOW zone generation from explicit ORB low source fields
- deterministic SWING_HIGH zone generation from explicit swing-high source fields
- deterministic SWING_LOW zone generation from explicit swing-low source fields
- no LTP-invented zones
- branch-local active_zone remains carried by MISR branch surface

MISR trap-event repair:

- `fake_break_start_ts_ms` must be explicitly supplied
- `fake_break_extreme_ts_ms` must be explicitly supplied
- missing fake-break timestamps now fail closed:
  - no fake_break
  - no trap_event_id
- `trap_event_id` is built from:
  - branch side
  - active_zone_id
  - fake_break_start_ts_ms
  - fake_break_extreme_ts_ms
- branch surface emits:
  - `fake_break_start_ts_ms`
  - `fake_break_extreme_ts_ms`
  - `fake_break_timestamps_valid`
  - `trap_event_id`
  - `trap_event_id_valid`

Consumed-event registry repair:

- pure helper added at `strategy_family/event_registry.py`
- no Redis mutation added
- no order mutation added
- MISR leaf blocks candidate if:
  - `trap_event_id` is missing
  - `trap_event_id` is already consumed
- consumed statuses covered:
  - ORDER_SENT
  - FILLED
  - CANCELED
  - TIMEOUT
  - REJECTED
  - FAILED
  - FLATTENED
  - CONSUMED

## Safety posture

- observe_only default unchanged
- paper_armed not approved
- real live not approved
- execution arming unchanged
- no Redis names added
- no risk/execution behavior changed
- no broker behavior changed

## Remaining outside this batch

- Batch 26G: MISO burst identity + microstructure repair
- Batch 25V market-session observe_only proof rerun
- Batch 25W paper_armed readiness gate rerun

Paper trading remains blocked until later gates pass.
