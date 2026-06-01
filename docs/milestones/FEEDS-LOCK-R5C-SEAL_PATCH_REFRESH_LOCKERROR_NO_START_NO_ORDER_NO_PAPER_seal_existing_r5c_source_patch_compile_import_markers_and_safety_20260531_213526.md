# FEEDS-LOCK-R5C-SEAL_PATCH_REFRESH_LOCKERROR_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_FEEDS_LOCK_R5C_SEALED_PATCH_REFRESH_LOCKERROR_SAFE_REACQUIRE_NO_START_NO_ORDER_NO_PAPER**

## Sealed patch

Target:

- `app/mme_scalpx/services/feeds.py`

R5C markers:

- `FEEDS_LOCK_R5C_REFRESH_LOCKERROR_SAFE_REACQUIRE`
- `except RX.LockError as exc`
- `feeds_lock_reacquired_after_refresh_error`
- `feeds singleton lock refresh failed after refresh LockError`

## Checks

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

## Artifacts

- Proof: `run/proofs/FEEDS-LOCK-R5C-SEAL_PATCH_REFRESH_LOCKERROR_NO_START_NO_ORDER_NO_PAPER_seal_existing_r5c_source_patch_compile_import_markers_and_safety_20260531_213526.json`
- Patch diff: `run/patches/FEEDS-LOCK-R5C-SEAL_PATCH_REFRESH_LOCKERROR_NO_START_NO_ORDER_NO_PAPER_seal_existing_r5c_source_patch_compile_import_markers_and_safety_20260531_213526_patch.diff`
- Source extract: `run/audits/FEEDS-LOCK-R5C-SEAL_PATCH_REFRESH_LOCKERROR_NO_START_NO_ORDER_NO_PAPER_seal_existing_r5c_source_patch_compile_import_markers_and_safety_20260531_213526_refresh_lock_if_due_extract.txt`
