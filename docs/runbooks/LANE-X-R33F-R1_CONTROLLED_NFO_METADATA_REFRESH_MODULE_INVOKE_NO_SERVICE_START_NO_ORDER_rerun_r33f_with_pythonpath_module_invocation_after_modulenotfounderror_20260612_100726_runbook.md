# LANE-X-R33F-R1_CONTROLLED_NFO_METADATA_REFRESH_MODULE_INVOKE_NO_SERVICE_START_NO_ORDER_rerun_r33f_with_pythonpath_module_invocation_after_modulenotfounderror_20260612_100726

classification: PASS_R33F_R1_CONTROLLED_NFO_METADATA_REFRESH_DONE_NO_SERVICE_START_NO_ORDER

## What happened

R33F failed only because `app` was not importable in file-path execution.
R33F-R1 reruns the same data-only metadata refresh using module invocation with PYTHONPATH.

## Validation

- refresh_rc: `0`
- rows: `42568`
- mtime_after_start: `true`
- stale_now: `false`
- restored_backup: `false`

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Boundary

- no source patch
- no service start
- no service stop
- no replay
- no broker order
- no risk/execution
- no Redis delete
- no lock delete

## Next

If PASS, do observe-only feeds reuse/restart and 60-second fut/opt tape growth proof.
