# LANE-X-R33F_CONTROLLED_NFO_METADATA_REFRESH_NO_SERVICE_START_NO_ORDER_refresh_stale_nfo_instruments_csv_data_only_with_backup_and_validation_20260612_100558

classification: REVIEW_R33F_NFO_METADATA_REFRESH_FAILED_OR_SAFETY_NONZERO

## What happened

Controlled data-only NFO instrument metadata refresh.

## Validation

- refresh_rc: `1`
- rows: `39402`
- mtime_after_start: `false`
- stale_now: `true`
- restored_backup: `true`

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
