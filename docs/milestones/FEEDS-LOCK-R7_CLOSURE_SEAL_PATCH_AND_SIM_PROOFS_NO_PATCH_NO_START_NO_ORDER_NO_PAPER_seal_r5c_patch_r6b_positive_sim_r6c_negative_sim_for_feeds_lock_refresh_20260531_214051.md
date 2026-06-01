# FEEDS-LOCK-R7_CLOSURE_SEAL_PATCH_AND_SIM_PROOFS_NO_PATCH_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_FEEDS_LOCK_R7_CLOSURE_SEALED_PATCH_AND_SIM_PROOFS_NO_PATCH_NO_START_NO_ORDER_NO_PAPER**

## Closure summary

The feeds singleton lock refresh timeout issue has been patched and simulated safely.

Target:

- `app/mme_scalpx/services/feeds.py`
- `FeedService.refresh_lock_if_due()`

Patch behavior:

- catches `RX.LockError` from `RX.refresh_lock()`
- if `lock:feeds` is absent, safe reacquire is allowed
- if reacquired after refresh error, publishes `feeds_lock_reacquired_after_refresh_error`
- if `lock:feeds` exists, no reacquire is attempted
- does not steal another owner's lock
- raises `FeedStartupError` from original `LockError` when recovery is unsafe

## Proof chain

- R4B patch plan: `run/proofs/FEEDS-LOCK-R4B_COMPACT_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_compact_plan_refresh_lockerror_safe_reacquire_20260531_212954.json`
- R5C patch seal: `run/proofs/FEEDS-LOCK-R5C-SEAL_PATCH_REFRESH_LOCKERROR_NO_START_NO_ORDER_NO_PAPER_seal_existing_r5c_source_patch_compile_import_markers_and_safety_20260531_213526.json`
- R6B positive simulation: `run/proofs/FEEDS-LOCK-R6B_DIRECT_METHOD_SIM_REFRESH_LOCKERROR_REACQUIRE_NO_START_NO_ORDER_NO_PAPER_simulate_refresh_lockerror_absent_lock_reacquire_without_full_feedservice_init_20260531_213750.json`
- R6C negative simulation: `run/proofs/FEEDS-LOCK-R6C_SIM_REFRESH_LOCKERROR_OTHER_OWNER_NO_REACQUIRE_NO_START_NO_ORDER_NO_PAPER_prove_refresh_lockerror_does_not_reacquire_when_lock_held_by_other_owner_20260531_213912.json`

## Checks

- compile_ok=1
- import_ok=1
- markers_ok=1
- proofs_ok=1
- class_chain_ok=1
- safety_ok=1

## Safety

- No patch in this batch
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

## Next recommended step

Only after explicit approval: observe-only feeds retry / pfeeds check, still no risk/execution/order/paper/live.
