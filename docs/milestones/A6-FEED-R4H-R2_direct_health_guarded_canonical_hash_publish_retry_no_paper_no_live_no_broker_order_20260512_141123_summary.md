# A6-FEED-R4H-R2 — Direct-health guarded canonical hash publish retry

Generated IST: `2026-05-12T14:11:23.811228+05:30`

## Verdict

`PASS_A6_FEED_R4H_R2_DIRECT_HEALTH_CANONICAL_HASH_PUBLISH_NO_PAPER_NO_LIVE_NO_BROKER_ORDER`

## Hash publish

- hash_publish_attempted: `True`
- hashes_written: `['state:provider_runtime:mme', 'state:feed:futures:active', 'state:feed:selected_option:active', 'state:feed:option_context:active', 'state:dhan_context:mme']`

## Guards

`{'approval_ok': True, 'dependency_ok': True, 'contract_ok': True, 'safety_before_ok': True, 'orders_zero': True, 'position_flat': True, 'no_risk_execution_order_pids': True, 'lock_feeds_stable_exact_value': True, 'lock_feeds_all_string': True, 'futures_stream_growing': True, 'selected_option_stream_growing': True, 'latest_futures_entry_exists': True, 'latest_selected_option_entry_exists': True, 'features_or_decisions_growing': True, 'allowed_hashes_exact': True}`

## Post hash presence

`{'provider_runtime_hash_present': True, 'active_futures_hash_present': True, 'selected_option_hash_present': True, 'option_context_hash_present': True, 'dhan_context_hash_present': True}`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- service_stop_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- broker_order_executed: false
- order_sent: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R5 canonical stream/hash post-publish feature-decision readiness proof / no paper / no order / no broker call`
