# B3-R46_ECONOMICS_AUTHORITY_FILTER_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER next route

Run:

`B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION`

Expected economics values:

- tick_size = 0.05
- target_points = 5.0
- stop_points = 4.0
- target_ticks = 100.0
- stop_ticks = 80.0
- reward_ticks = 100.0
- reward_cost_ratio = 1.25

Also verify:

- strategy_rows unchanged
- candidate_rows unchanged
- replay integrity pass
- no Redis/live/broker/order/paper/risk/execution
