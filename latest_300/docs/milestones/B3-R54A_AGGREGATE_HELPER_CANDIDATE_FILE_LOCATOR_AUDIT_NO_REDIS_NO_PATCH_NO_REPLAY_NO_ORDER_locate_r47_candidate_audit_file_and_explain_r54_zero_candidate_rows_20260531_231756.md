# B3-R54A_AGGREGATE_HELPER_CANDIDATE_FILE_LOCATOR_AUDIT_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER

Classification: `PASS_R54A_ROOT_CAUSE_HELPER_CHOSE_DIR_WITHOUT_CANDIDATE_AUDIT_PATCH_PLAN_NEEDED`

R54 created aggregate files but candidate rows were zero. This audit locates the real R47 candidate audit file and explains the mismatch.

Best candidate file: `{'pattern': '*candidate*audit*.csv', 'path': 'run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/06_candidate_audit.csv', 'parent': 'run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42', 'name': '06_candidate_audit.csv', 'size': 1051446, 'rows': 5887, 'header': ['row_index', 'event_time', 'source_frame_id', 'action', 'candidate', 'candidate_fallback', 'selected_leg', 'side', 'linked_feature_side', 'metadata_side', 'blocker_name', 'blocker_reason', 'blocker_reason_fallback', 'economics_reason', 'reason']}`

No Redis, no replay, no patch, no broker/order/paper/live/risk/execution.
