# A6-FEED-R4E — Observe-only feed health restore plan

Generated IST: `2026-05-12T13:44:45.008519+05:30`

## Verdict

`PASS_A6_FEED_R4E_OBSERVE_ONLY_FEED_HEALTH_RESTORE_PLAN_READY_NO_START_NO_HASH_PUBLISH_NO_ORDER`

## Restore plan

- restore_plan_type: `RESTART_OBSERVE_ONLY_FEEDS_AND_RECHECK_LOCK_STREAMS`
- restore_root_cause: `FEEDS_PROCESS_PRESENT_BUT_HEALTH_LOCK_AND_STREAMS_LOST`

## Classification inputs

`{'feeds_process_present': True, 'features_process_present': True, 'strategy_process_present': True, 'pfeedcheck_healthy_recording': False, 'feed_lock_present': False, 'fut_growing': False, 'selected_growing': False, 'features_growing': True, 'decisions_growing': True}`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- service_stop_attempted: false
- hash_publish_attempted: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Fresh approval required for next action

`I APPROVE A6-FEED-R4F OBSERVE-ONLY FEED HEALTH RESTORE ACTION: NO PAPER, NO LIVE, NO BROKER ORDER, NO RISK/EXECUTION START, NO SOURCE PATCH`

## Next

`A6-FEED-R4F observe-only feed health restore action / requires fresh approval`
