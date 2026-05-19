# A6-LIVE-R2I-D2 — Compact proof recovery and provider-not-ready classifier

Generated IST: `2026-05-12T10:28:46.081646+05:30`

## Verdict

`PASS_A6_LIVE_R2I_D2_COMPACT_ROOT_CAUSE_CLASSIFIED_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`

## Root cause

`VIEW_DATA_INVALID_DUE_PROVIDER_NOT_READY_IN_FAMILY_SURFACES`

## Prior R2I-D recovery

- exists: `True`
- recovered: `True`
- prior_final_verdict: `PASS_A6_LIVE_R2I_D_VIEW_DATA_INVALID_ROOT_CAUSE_CLASSIFIED_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`
- prior_root_cause: `VIEW_DATA_INVALID_DUE_SAFE_TO_CONSUME_FALSE`

## Compact evidence

- reason_counts: `{'hold_only_family_features_consumer_bridge': 20, 'None': 60}`
- activation_reason_counts: `{'view_data_invalid': 20, 'None': 60}`
- provider_not_ready_path_count: `10`
- not_present_path_count: `13`
- stale_path_count: `45`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-LIVE-R2I-E provider/feed surface recovery diagnostic / no source patch / no order / no broker call`
