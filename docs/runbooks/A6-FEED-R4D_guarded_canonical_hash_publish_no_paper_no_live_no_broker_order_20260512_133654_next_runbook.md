# A6-FEED-R4D next runbook

## Current status

`BLOCKED_A6_FEED_R4D_GUARDS_FAILED_NO_HASH_PUBLISH_NO_ORDER_NO_BROKER`

## Next

`A6-FEED-R4D-D guard failure diagnostic / no hash publish / no order / no broker call`

## Rule

If PASS, run A6-FEED-R5 to verify that features/decisions consume the newly published canonical provider/feed hashes.
Do not run A6-PAPER until A6-FEED-R5 proves readiness.
