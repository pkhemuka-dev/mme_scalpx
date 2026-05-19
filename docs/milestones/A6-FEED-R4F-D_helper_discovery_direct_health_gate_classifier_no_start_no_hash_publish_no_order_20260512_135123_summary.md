# A6-FEED-R4F-D — Helper discovery + direct health gate classifier

Generated IST: `2026-05-12T13:51:23.233809+05:30`

## Verdict

`PASS_A6_FEED_R4F_D_HELPER_DISCOVERY_DIRECT_HEALTH_CLASSIFIED_NO_START_NO_HASH_PUBLISH_NO_ORDER`

## Root cause

`HELPER_DISCOVERY_MISSING_BUT_DIRECT_FEED_HEALTH_OK`

## Direct feed health

`{'direct_health_ok': True, 'fut_growing': True, 'selected_growing': True, 'context_growing': True, 'features_growing': True, 'decisions_growing': True, 'lock_feeds_string_present': True, 'lock_feeds_value': 'feeds:mme-scalpx:370292'}`

## Helper detection

`{'pfeed_found_any_shell': False, 'pfeedcheck_healthy_any_shell': True}`

## Safety

- hash_publish_attempted: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false

## Next

`A6-FEED-R4G direct-health guarded canonical hash publish plan / no hash publish until approved`
