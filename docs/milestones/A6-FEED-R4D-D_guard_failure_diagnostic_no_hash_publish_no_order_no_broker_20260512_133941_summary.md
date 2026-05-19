# A6-FEED-R4D-D — Guard failure diagnostic

Generated IST: `2026-05-12T13:39:41.914356+05:30`

## Verdict

`PASS_A6_FEED_R4D_D_GUARD_FAILURE_CLASSIFIED_NO_HASH_PUBLISH_NO_ORDER_NO_BROKER`

## Root cause

`FEED_HEALTH_AND_LOCK_LOST_BEFORE_R4D_HASH_PUBLISH`

## Classification inputs

`{'feeds_process_present': True, 'pfeedcheck_healthy_recording': False, 'feed_lock_present': False, 'fut_growing': False, 'selected_growing': False, 'features_growing': True, 'decisions_growing': True}`

## Safety

- hash_publish_attempted: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-FEED-R4E observe-only feed health restore plan / no start until approved`
