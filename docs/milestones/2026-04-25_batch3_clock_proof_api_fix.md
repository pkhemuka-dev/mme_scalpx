# Batch 3 — Clock Proof API Fix

Date: 2026-04-25 09:50:05 IST

## Problem

`bin/proof_clock_session_policy.py` called non-existent API:

- `clock.market_phase_at()`

Actual clock API is:

- `clock.market_phase_from_ist_datetime()`
- `clock.can_enter_new_positions()`
- `clock.is_regular_market_session_open()`

## Fix

The proof was rewritten to use the actual `clock.py` API.

## Result required

Batch 3 can be marked freeze-final only if all pass:

- `bin/proof_core_codec_transport.py`
- `bin/proof_redisx_typed_stream_helpers.py`
- `bin/proof_runtime_effective_config.py`
- `bin/proof_clock_session_policy.py`
- `bin/proof_redis_contract_matrix.py --strict-raw`

## Boundary

`clock.py` itself was not rewritten.

Fresh-entry policy remains:

- generic clock helper: `can_enter_new_positions()`
- family-specific stricter timing: owned by strategy/risk/session policy, not `clock.py`

