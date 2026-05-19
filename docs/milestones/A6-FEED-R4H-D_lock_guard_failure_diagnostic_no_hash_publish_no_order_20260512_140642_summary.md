# A6-FEED-R4H-D — Lock guard failure diagnostic

Generated IST: `2026-05-12T14:06:42.805376+05:30`

## Verdict

`PASS_A6_FEED_R4H_D_LOCK_GUARD_FAILURE_CLASSIFIED_NO_HASH_PUBLISH_NO_ORDER`

## Root cause

`R4H_LOCK_GUARD_TRANSIENT_FAILURE_NOW_STABLE`

## Lock summary

- all_string: `True`
- any_missing: `False`
- stable_exact_value: `True`
- stable_owner_prefix: `True`
- unique_value_count: `1`
- owner_prefixes: `['feeds:mme-scalpx']`

## Direct health

`{'direct_health_ok': True, 'fut_growing': True, 'selected_growing': True, 'context_growing': True, 'features_growing': False, 'decisions_growing': True}`

## Safety

- hash_publish_attempted: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false

## Next

`A6-FEED-R4H-R2 direct-health guarded canonical hash publish retry / requires same approval`
