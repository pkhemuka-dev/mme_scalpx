# B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION

Classification: `PASS_R44_ECONOMICS_ENRICHMENT_GENERATED_AND_REPLAY_COUNTS_STABLE`  
Created: `2026-05-31T21:52:57.315227+05:30`

## Replay

- Return code: `0`
- Integrity verdict: `pass`
- Latest run: `run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f`

## Counts

- strategy rows: `5887`
- features rows: `5887`
- candidate rows: `5887`
- row counts OK: `True`

## Economics enrichment

- schema: `b3_r43_economics_export_enrichment_v1`
- status: `enriched_source_labelled`
- enriched values: `{'entry_mode': 'NO_ENTRY_HOLD_ONLY', 'reward_points': 0.0, 'stop_points': 0.0, 'target_points': 0.0, 'tick_size': 0.0}`
- fields left missing: `['target_ticks', 'stop_ticks', 'reward_ticks', 'reward_cost_ratio']`

## Safety

Offline replay smoke only. No Redis. No broker/order/paper/live/risk/execution.
