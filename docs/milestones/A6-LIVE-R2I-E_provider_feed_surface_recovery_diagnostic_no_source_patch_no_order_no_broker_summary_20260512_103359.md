# A6-LIVE-R2I-E — Provider/feed surface recovery diagnostic

Generated IST: `2026-05-12T10:33:59.199951+05:30`

## Verdict

`PASS_A6_LIVE_R2I_E_PROVIDER_FEED_SURFACE_RECOVERY_CLASSIFIED_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`

## Root cause

`ACTIVE_FUTURES_FEED_NOT_REACHING_RUNTIME_SURFACE`

## Classification inputs

- fut_growing: `False`
- selected_option_growing: `False`
- option_context_growing: `False`
- feature_growing: `True`
- decision_growing: `True`
- provider_runtime_hash_present: `False`
- active_futures_hash_present: `False`
- selected_option_hash_present: `False`
- option_context_hash_present: `False`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-LIVE-R2I-F active-futures feed/runtime recovery diagnostic / no source patch / no order / no broker call`
