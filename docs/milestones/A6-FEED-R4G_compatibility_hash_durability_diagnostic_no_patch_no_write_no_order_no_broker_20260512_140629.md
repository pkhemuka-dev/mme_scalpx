# A6-FEED-R4G_compatibility_hash_durability_diagnostic_no_patch_no_write_no_order_no_broker_20260512_140629

## Purpose
Compatibility hash durability diagnostic after R4F/R5 mismatch.

## Verdict
PASS_A6_FEED_R4G_COMPAT_HASH_DURABILITY_GAP_CONFIRMED_NO_PATCH_NO_WRITE

## Exact blocker
SOURCE_CANON_HASHES_PRESENT_BUT_A6_COMPAT_HASHES_ABSENT_OR_NOT_DURABLE

## Safety
- source_patch_applied: false
- redis_hash_write_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Key checks
- compat_present_before: False
- compat_present_after_30: False
- source_present_after_30: True

## Next
A6-FEED-R4H
