# A6-LIVE-R2I-D — View-data-invalid root-cause diagnostic

Generated IST: `2026-05-12T10:24:16.823611+05:30`

## Verdict

`PASS_A6_LIVE_R2I_D_VIEW_DATA_INVALID_ROOT_CAUSE_CLASSIFIED_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`

## Root cause

`VIEW_DATA_INVALID_DUE_SAFE_TO_CONSUME_FALSE`

## Key counts

- reason_counts: `{'hold_only_family_features_consumer_bridge': 120, 'None': 180}`
- activation_reason_counts: `{'view_data_invalid': 120, 'None': 180}`
- false_counts: `{'data_valid': 120, 'provider_ready_classic': 120, 'provider_ready_miso': 120, 'activation_safe_to_promote': 120, 'activation_candidate_count': 120, 'consumer_view_json.data_valid': 200, 'consumer_view_json.provider_ready_classic': 200, 'consumer_view_json.provider_ready_miso': 200, 'payload_json.data_valid': 120, 'payload_json.provider_ready_classic': 120, 'payload_json.provider_ready_miso': 120, 'payload_json.activation_safe_to_promote': 120, 'payload_json.activation_candidate_count': 120, 'consumer_view_json.safe_to_consume': 80}`
- true_counts: `{'warmup_complete': 120, 'safe_to_consume': 120, 'activation_bridge_enabled': 120, 'consumer_view_json.warmup_complete': 200, 'consumer_view_json.safe_to_consume': 120, 'payload_json.warmup_complete': 120, 'payload_json.safe_to_consume': 120, 'payload_json.activation_bridge_enabled': 120}`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-LIVE-R2I-E readiness/provider specific diagnostic / no source patch / no order / no broker call`
