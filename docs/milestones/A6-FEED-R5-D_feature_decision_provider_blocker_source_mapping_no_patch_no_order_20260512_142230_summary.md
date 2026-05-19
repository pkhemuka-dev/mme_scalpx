# A6-FEED-R5-D — Feature-decision provider-blocker source mapping

Generated IST: `2026-05-12T14:22:30.416135+05:30`

## Verdict

`PASS_A6_FEED_R5_D_PROVIDER_BLOCKER_SOURCE_MAPPED_NO_PATCH_NO_ORDER`

## Root cause

`CANONICAL_HASHES_DISAPPEARED_OR_NOT_IN_CURRENT_REDIS_AFTER_R4H_R2`

## Required hash presence

`{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Required hash types

`{'state:provider_runtime:mme': 'none', 'state:feed:futures:active': 'none', 'state:feed:selected_option:active': 'none', 'state:feed:option_context:active': 'none', 'state:dhan_context:mme': 'none'}`

## Provider hits

- total: `70`
- post_publish: `70`
- old_or_unknown: `0`

## Classification inputs

`{'all_required_absent_now': True, 'post_publish_consumer_blocked': True, 'scan_shows_alt_feed_keys': True, 'r4_dependency_ok': True, 'r5_dependency_ok': True}`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- service_stop_attempted: false
- hash_publish_attempted: false
- broker_order_executed: false
- order_sent: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R5-E canonical hash persistence/keyspace diagnostic / no patch / no order`
