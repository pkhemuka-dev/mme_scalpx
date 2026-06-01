# B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION

Classification: `PASS_R47_AUTHORITY_FILTER_ECONOMICS_ENRICHMENT_VALUES_MATCH_EXPECTED`  
Created: `2026-05-31T22:39:16.375667+05:30`

## Replay

- Return code: `0`
- Integrity verdict: `pass`
- Latest run: `run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42`

## Counts

- strategy rows: `5887`
- features rows: `5887`
- candidate rows: `5887`
- row counts OK: `True`

## Economics enrichment

Expected:

`{'tick_size': 0.05, 'target_points': 5.0, 'stop_points': 4.0, 'reward_points': 5.0, 'target_ticks': 100.0, 'stop_ticks': 80.0, 'reward_ticks': 100.0, 'reward_cost_ratio': 1.25}`

Actual:

`{'entry_mode': 'NO_ENTRY_HOLD_ONLY', 'reward_cost_ratio': 1.25, 'reward_points': 5.0, 'reward_ticks': 100.0, 'stop_points': 4.0, 'stop_ticks': 80.0, 'target_points': 5.0, 'target_ticks': 100.0, 'tick_size': 0.05}`

Expected match:

`{'tick_size': True, 'target_points': True, 'stop_points': True, 'reward_points': True, 'target_ticks': True, 'stop_ticks': True, 'reward_ticks': True, 'reward_cost_ratio': True}`

Bad zero/default authority present: `False`

## Safety

Offline replay smoke only. No Redis. No broker/order/paper/live/risk/execution.
