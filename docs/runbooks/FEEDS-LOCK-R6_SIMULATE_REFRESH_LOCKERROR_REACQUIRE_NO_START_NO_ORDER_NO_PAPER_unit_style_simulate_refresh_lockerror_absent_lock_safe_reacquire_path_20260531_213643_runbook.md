# FEEDS-LOCK-R6_SIMULATE_REFRESH_LOCKERROR_REACQUIRE_NO_START_NO_ORDER_NO_PAPER

Classification: **FAIL_FEEDS_LOCK_R6_SIMULATION_CHECK_FAILED**

## Simulation

Simulated:

- `RX.refresh_lock()` raises `RX.LockError`
- `lock:feeds` type returns `none`
- `RX.acquire_lock()` returns `True`

Expected:

- `refresh_lock_if_due()` recovers
- `_last_lock_refresh_ns` updates
- event `feeds_lock_reacquired_after_refresh_error` is published

Simulation artifact:

- `run/audits/FEEDS-LOCK-R6_SIMULATE_REFRESH_LOCKERROR_REACQUIRE_NO_START_NO_ORDER_NO_PAPER_unit_style_simulate_refresh_lockerror_absent_lock_safe_reacquire_path_20260531_213643_simulation.json`

## Checks

- simulation_ok=0
- compile_ok=1
- import_ok=1
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
