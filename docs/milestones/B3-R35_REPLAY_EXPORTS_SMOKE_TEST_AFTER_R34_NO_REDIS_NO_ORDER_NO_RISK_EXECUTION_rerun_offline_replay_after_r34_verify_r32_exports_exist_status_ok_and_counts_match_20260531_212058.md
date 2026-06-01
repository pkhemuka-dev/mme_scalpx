# B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION

Classification: `BLOCKED_R35_REPLAY_PASS_BUT_EXPORTS_STILL_MISSING`  
Created: `2026-05-31T21:21:05.742485+05:30`

## Replay

- Return code: `0`
- Latest run dir: `run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea`
- Integrity verdict: `pass`

## Rows

- strategy rows: `5887`
- features rows: `5887`
- candidate row match: `False`

## Exports

`{'candidate_audit': {'exists': False, 'path': None, 'rows': None, 'header': []}, 'blocker_distribution': {'exists': True, 'path': 'run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/blocker_distribution.csv', 'rows': 0, 'header': ['blocker_key', 'blocker_name', 'blocker_reason', 'blocker_reason_fallback', 'economics_reason', 'reason', 'side', 'selected_leg', 'count']}, 'economics_summary': {'exists': True, 'path': 'run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/economics_summary.json', 'payload_keys': ['economics_reason_counts', 'field_presence', 'missing_economics_fields', 'note', 'row_count', 'schema_version', 'selected_leg_counts', 'value_counts'], 'missing_economics_fields': ['source_frame_id', 'selected_leg', 'entry_mode', 'tick_size', 'target_ticks', 'stop_ticks', 'reward_ticks', 'reward_cost_ratio', 'economics_reason'], 'selected_leg_counts': {}, 'economics_reason_counts': {}}, 'family_side_summary': {'exists': True, 'path': 'run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/family_side_summary.csv', 'rows': 0, 'header': ['family', 'side', 'linked_feature_side', 'metadata_side', 'selected_leg', 'count', 'decode_quality']}, 'status': {'exists': True, 'path': 'run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/b3_r32_analysis_exports_status.json', 'payload': {'blocker_distribution_rows': 0, 'candidate_audit_rows': 0, 'economics_missing_fields': ['source_frame_id', 'selected_leg', 'entry_mode', 'tick_size', 'target_ticks', 'stop_ticks', 'reward_ticks', 'reward_cost_ratio', 'economics_reason'], 'family_side_summary_rows': 0, 'features_rows': 0, 'features_rows_path': 'run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/features_rows.json', 'schema_version': 'b3_r32_analysis_exports_status_v1', 'status': 'ok', 'strategy_decisions_path': 'run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/strategy_decisions.json', 'strategy_rows': 0}}, 'error': {'exists': False, 'path': None, 'payload': None}}`

## Safety

Offline replay smoke only. No Redis. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058.json`
- Latest proof: `run/proofs/B3_R35_latest.json`
- Audit: `run/audits/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_audit.json`
- Log: `run/logs/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_replay_runner.log`
