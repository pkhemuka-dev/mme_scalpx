# A6-LIVE-R2I-F — Active futures feed/runtime recovery diagnostic

Generated IST: `2026-05-12T10:36:11.715472+05:30`

## Verdict

`PASS_A6_LIVE_R2I_F_ACTIVE_FUTURES_FEED_RUNTIME_ROOT_CAUSE_CLASSIFIED_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`

## Root cause

`FEEDS_PROCESS_PRESENT_BUT_PROVIDER_FEED_ERRORS_VISIBLE`

## Classification inputs

- feeds_process_present: `True`
- features_process_present: `True`
- strategy_process_present: `True`
- provider_process_present: `False`
- futures_streams_zero: `True`
- selected_streams_zero: `True`
- context_stream_zero: `True`
- provider_runtime_hash_present: `False`
- active_futures_hash_present: `False`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-LIVE-R2I-G feed provider error classifier / no source patch / no order / no broker call`
