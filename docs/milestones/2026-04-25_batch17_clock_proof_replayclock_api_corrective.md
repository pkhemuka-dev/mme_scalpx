# Batch 17 — Clock Proof ReplayClock API Corrective

Date: 2026-04-25 12:11:03 IST

## Problem

Batch 17 research-capture proof, codec proof, redisx proof, runtime-config proof, and strict Redis regression passed, but prior regression smoke stopped at:

```text
ReplayClock.__init__() got an unexpected keyword argument 'initial_wall_time_ns'
```

## Root cause

`bin/proof_clock_session_policy.py` used stale ReplayClock constructor names:

- `initial_wall_time_ns`
- `initial_monotonic_ns`
- `strict_monotonic`

Current `clock.py` uses:

- `start_wall_time_ns`
- `start_monotonic_ns`
- `strict_monotonicity`

The proof also used old two-argument `advance_both_ns(500, 10)`. Current `advance_both_ns()` accepts one delta, so the proof now uses `set_both_ns(wall_time_ns=1500, monotonic_ns=510)`.

## Fix

Proof-only patch. `clock.py` was not changed.

## Result required

Batch 17 is freeze-final only after:

- `bin/proof_clock_session_policy.py` returns PASS
- `bin/proof_research_capture_contracts.py` returns PASS
- `bin/proof_redis_contract_matrix.py --strict-raw` returns PASS
- prior batch regression smoke returns PASS

