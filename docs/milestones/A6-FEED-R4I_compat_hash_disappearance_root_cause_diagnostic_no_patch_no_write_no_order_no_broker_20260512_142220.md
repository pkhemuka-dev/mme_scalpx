# A6-FEED-R4I_compat_hash_disappearance_root_cause_diagnostic_no_patch_no_write_no_order_no_broker_20260512_142220

## Purpose
Read-only diagnostic for disappearing / non-durable A6-FEED compatibility hashes.

## Verdict
PASS_A6_FEED_R4I_COMPATIBILITY_PUBLISHER_SOURCE_SEAM_REQUIRED_NO_PATCH_NO_WRITE

## Exact blocker
LIVE_SOURCE_HASHES_DURABLE_BUT_A6_COMPAT_HASHES_NOT_PERIODICALLY_PUBLISHED

## Safety
- source_patch_applied: false
- redis_hash_write_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Key checks
- compat_present_t0: False
- compat_present_t40: False
- source_present_t40: True
- feed_ok: True

## Next
A6-FEED-R4J
