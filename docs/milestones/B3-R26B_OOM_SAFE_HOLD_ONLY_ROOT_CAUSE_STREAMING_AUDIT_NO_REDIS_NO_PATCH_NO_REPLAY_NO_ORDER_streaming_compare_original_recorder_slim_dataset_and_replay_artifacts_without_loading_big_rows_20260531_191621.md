# B3-R26B_OOM_SAFE_HOLD_ONLY_ROOT_CAUSE_STREAMING_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R26B_OOM_SAFE_HOLD_ONLY_ROOT_CAUSE_SAMPLE_NO_CANDIDATE`  
Root cause: `SAMPLED_ORIGINAL_SLIM_AND_REPLAY_ARE_HOLD_ONLY_NO_CANDIDATE`  
Created: `2026-05-31T19:22:05.257318+05:30`

## Summary

`{'recorder_dir': 'run/live_capture/B1-PROFIT-LIVE-R37M_LIVE_SESSION_EMERGENCY_DURABLE_RECORDER_NO_ORDER_start_readonly_redis_stream_recorder_without_restart_no_risk_no_execution_no_order_20260527_092428', 'original_decisions_rows_scanned': 5000, 'original_decision_action_counts': {'HOLD': 5000}, 'original_decision_candidate_hits': 0, 'slim_decision_rows_scanned': 1844, 'slim_decision_action_counts': {'HOLD': 1844}, 'slim_decision_candidate_hits': 0, 'replay_strategy_rows_scanned': 5887, 'replay_strategy_action_counts': {'HOLD': 5887}, 'replay_strategy_candidate_hits': 0, 'replay_strategy_economics_presence': {'source_frame_id': 5887, 'selected_leg': 3646, 'economics_reason': 5887}, 'replay_features_economics_presence': {'source_frame_id': 5887, 'selected_leg': 3646}, 'keyword_hits': {'original_decisions': {'MIST': 5000, 'PUT': 5000, 'CALL': 5000, 'candidate': 5000, 'entry': 5000, 'eligible': 5000, 'blocker': 3875}, 'slim_decisions': {'MIST': 1844, 'PUT': 1394, 'CALL': 1394, 'candidate': 1844, 'blocker': 1394}, 'replay_strategy': {'candidate': 5887, 'entry': 5887, 'blocker': 5887, 'selected_leg': 5887, 'economics_reason': 5887, 'CALL': 1543, 'PUT': 1453}}}`

## Safety

OOM-safe offline artifact audit only. No Redis. No replay. No patch. No service action. No broker/order/paper/live/risk/execution.

## Artifacts

- Proof: `run/proofs/B3-R26B_OOM_SAFE_HOLD_ONLY_ROOT_CAUSE_STREAMING_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_streaming_compare_original_recorder_slim_dataset_and_replay_artifacts_without_loading_big_rows_20260531_191621.json`
- Latest proof: `run/proofs/B3_R26B_latest.json`
- Audit: `run/audits/B3-R26B_OOM_SAFE_HOLD_ONLY_ROOT_CAUSE_STREAMING_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_streaming_compare_original_recorder_slim_dataset_and_replay_artifacts_without_loading_big_rows_20260531_191621_audit.json`
