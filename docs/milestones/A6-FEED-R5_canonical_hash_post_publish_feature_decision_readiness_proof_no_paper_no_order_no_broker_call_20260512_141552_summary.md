# A6-FEED-R5 — Canonical hash post-publish feature-decision readiness proof

Generated IST: `2026-05-12T14:15:52.308423+05:30`

## Verdict

`BLOCKED_A6_FEED_R5_FEATURE_DECISION_STILL_SHOW_PROVIDER_BLOCKER_NO_PAPER_NO_ORDER`

## Readiness assertions

`{'dependency_ok': True, 'safety_ok': True, 'all_required_hashes_present': False, 'all_required_hashes_ready': False, 'futures_stream_growing': True, 'selected_option_stream_growing': True, 'option_context_stream_growing': True, 'features_or_decisions_growing': True, 'no_provider_not_ready_or_view_data_invalid_in_recent_samples': False, 'orders_zero': True, 'position_flat': True, 'no_risk_execution_order_pids': True}`

## Required hash presence

`{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Required hash ready

`{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Provider blocker hits

`['provider_not_ready', 'view_data_invalid']`

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

`A6-FEED-R5-D feature-decision provider-blocker source mapping / no patch / no order`
