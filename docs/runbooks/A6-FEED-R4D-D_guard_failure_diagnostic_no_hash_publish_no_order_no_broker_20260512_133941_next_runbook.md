# A6-FEED-R4D-D next runbook

## Status

`PASS_A6_FEED_R4D_D_GUARD_FAILURE_CLASSIFIED_NO_HASH_PUBLISH_NO_ORDER_NO_BROKER`

## Root cause

`FEED_HEALTH_AND_LOCK_LOST_BEFORE_R4D_HASH_PUBLISH`

## Next

`A6-FEED-R4E observe-only feed health restore plan / no start until approved`

## Rule

Do not rerun hash publish until pfeedcheck is HEALTHY_RECORDING, lock:feeds is stable string, futures/selected option streams are growing, and safety is clean.
