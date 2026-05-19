# A6-FEED-R4H next runbook

## Status

`BLOCKED_A6_FEED_R4H_GUARDS_FAILED_NO_HASH_PUBLISH_NO_ORDER_NO_BROKER`

## Next

`A6-FEED-R4H-D guard failure diagnostic / no hash publish / no order`

## Rule

If PASS, run A6-FEED-R5 to prove features/decisions consume the canonical hashes and no longer produce provider_not_ready/view_data_invalid.
Do not continue A6-PAPER until A6-FEED-R5 passes.
