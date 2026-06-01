# FEEDS-LOCK-R6C_SIM_REFRESH_LOCKERROR_OTHER_OWNER_NO_REACQUIRE_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_FEEDS_LOCK_R6C_SIM_LOCKERROR_OTHER_OWNER_NO_REACQUIRE_NO_START_NO_ORDER_NO_PAPER**

## Negative simulation

Simulated:

- `RX.refresh_lock()` raises `RX.LockError`
- `lock:feeds` type returns `string`, meaning lock exists / may belong to another owner
- `RX.acquire_lock()` was patched to record calls

Expected:

- `refresh_lock_if_due()` must not reacquire
- acquire call count must remain 0
- `_last_lock_refresh_ns` must not update
- no recovery event should be published
- `FeedStartupError` should be raised from original `RX.LockError`

Artifact:

- `run/audits/FEEDS-LOCK-R6C_SIM_REFRESH_LOCKERROR_OTHER_OWNER_NO_REACQUIRE_NO_START_NO_ORDER_NO_PAPER_prove_refresh_lockerror_does_not_reacquire_when_lock_held_by_other_owner_20260531_213912_simulation.json`

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
