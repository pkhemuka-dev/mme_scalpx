# A6-FEED-R4F — Observe-only feed health restore action

Generated IST: `2026-05-12T13:48:25.074273+05:30`

## Verdict

`FAIL_A6_FEED_R4F_RESTORE_PRECONDITIONS_FAILED_NO_START_NO_ORDER_NO_BROKER_ORDER`

## Restore action

- restore_attempted: `False`
- service_stop_attempted: `False`
- service_start_attempted: `False`
- source_patch_applied: false
- hash_publish_attempted: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- broker_order_executed: false
- order_sent: false

## Post assertions

`{'restore_attempted': False, 'safety_after_restore_ok': True, 'pfeedcheck_all_healthy_recording': False, 'healthy_recording_check_count_is_3': False, 'lock_feeds_stable_string': True, 'futures_stream_growing': True, 'selected_option_stream_growing': True, 'features_or_decisions_growing': True, 'orders_remain_zero': True, 'position_remains_flat': True, 'risk_execution_not_running': True, 'source_patch_applied_false': True, 'hash_publish_attempted_false': True, 'broker_order_attempted_false': True, 'order_sent_false': True}`

## Key recovery facts

- healthy_recording_check_count: `0`
- lock_feeds_stable_string: `True`
- futures_stream_growing: `True`
- selected_option_stream_growing: `True`
- option_context_stream_growing: `True`
- features_growing: `True`
- decisions_growing: `True`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R4F-D precondition diagnostic / no start / no order / no broker order`
