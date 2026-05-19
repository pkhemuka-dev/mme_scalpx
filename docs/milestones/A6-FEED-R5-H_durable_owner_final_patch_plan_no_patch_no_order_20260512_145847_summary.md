# A6-FEED-R5-H — Durable owner final patch plan

Generated IST: `2026-05-12T14:58:47.925107+05:30`

## Verdict

`PASS_A6_FEED_R5_H_DURABLE_OWNER_FINAL_PATCH_PLAN_READY_NO_PATCH_NO_ORDER`

## Root cause

`REQUIRED_CANONICAL_HASHES_STILL_NOT_DURABLY_PRESENT`

## Patch plan type

`MINIMAL_DURABLE_FEEDS_OWNER_PATCH_PLAN_AFTER_APPROVAL`

## Classification inputs

`{'all_hashes_present_now': False, 'all_hashes_ready_now': False, 'provider_blockers_now': True, 'futures_stream_growing': True, 'selected_stream_growing': True, 'context_stream_growing': False, 'features_growing': True, 'decisions_growing': True, 'dependency_ok': True, 'contract_ok': True}`

## Hash presence now

`{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': True, 'state:dhan_context:mme': False}`

## Hash ready now

`{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Consumer provider blocker count

`45`

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

`A6-FEED-R5-I minimal durable canonical hash owner patch plan / no patch until approved`
