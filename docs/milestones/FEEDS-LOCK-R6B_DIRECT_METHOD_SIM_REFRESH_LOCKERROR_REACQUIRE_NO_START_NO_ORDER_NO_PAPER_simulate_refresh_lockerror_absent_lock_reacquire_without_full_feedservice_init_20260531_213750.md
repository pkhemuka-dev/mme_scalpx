# FEEDS-LOCK-R6B_DIRECT_METHOD_SIM_REFRESH_LOCKERROR_REACQUIRE_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_FEEDS_LOCK_R6B_SIM_REFRESH_LOCKERROR_SAFE_REACQUIRE_NO_START_NO_ORDER_NO_PAPER**

## Simulation

Direct-method simulation using `FeedService.__new__()`, avoiding full service startup.

Simulated:

- `RX.refresh_lock()` raises `RX.LockError`
- `lock:feeds` type returns `none`
- `RX.acquire_lock()` returns `True`

Expected:

- `refresh_lock_if_due()` recovers
- `_last_lock_refresh_ns` updates
- event `feeds_lock_reacquired_after_refresh_error` is published

Artifact:

- `run/audits/FEEDS-LOCK-R6B_DIRECT_METHOD_SIM_REFRESH_LOCKERROR_REACQUIRE_NO_START_NO_ORDER_NO_PAPER_simulate_refresh_lockerror_absent_lock_reacquire_without_full_feedservice_init_20260531_213750_simulation.json`

## Checks

- simulation_ok=1
- compile_ok=1
- import_ok=1
- markers_ok=1
- safety_ok=1

## Safety

- No Redis write
- No service start/stop
- No broker call
- No order
- No paper/live

Safety counters:

- orders_before=0
- orders_after=0
- risk_stream_after=0
- execution_stream_after=0
- risk_pids_after=0
- execution_pids_after=0
