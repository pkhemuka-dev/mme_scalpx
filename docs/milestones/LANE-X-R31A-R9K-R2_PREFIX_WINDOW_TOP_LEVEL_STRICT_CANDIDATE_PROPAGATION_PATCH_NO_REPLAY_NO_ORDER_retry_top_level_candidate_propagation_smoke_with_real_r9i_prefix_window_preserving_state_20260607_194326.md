# LANE-X-R31A-R9K-R2_PREFIX_WINDOW_TOP_LEVEL_STRICT_CANDIDATE_PROPAGATION_PATCH_NO_REPLAY_NO_ORDER_retry_top_level_candidate_propagation_smoke_with_real_r9i_prefix_window_preserving_state_20260607_194326

classification: REVIEW_LANE_X_R31A_R9K_R2_PATCH_OR_SMOKE_FAILED_RESTORED_IF_NEEDED_NO_REPLAY_NO_ORDER

- pre_safe: 1
- patch_rc: 0
- patch_applied: 1
- compile_rc: 0
- smoke_rc: 1
- restored: 1
- marker_count: 0
0
- propagation_marker_count: 0
0
- post_orders: 0
- post_risk_stream: 0
- post_execution_stream: 0
- backup: `run/_code_backups/LANE-X-R31A-R9K-R2_PREFIX_WINDOW_TOP_LEVEL_STRICT_CANDIDATE_PROPAGATION_PATCH_NO_REPLAY_NO_ORDER_retry_top_level_candidate_propagation_smoke_with_real_r9i_prefix_window_preserving_state_20260607_194326_bin_replay_run.py.bak`
- patch_log: `run/audits/LANE-X-R31A-R9K-R2_PREFIX_WINDOW_TOP_LEVEL_STRICT_CANDIDATE_PROPAGATION_PATCH_NO_REPLAY_NO_ORDER_retry_top_level_candidate_propagation_smoke_with_real_r9i_prefix_window_preserving_state_20260607_194326_patch.log`
- smoke_log: `run/audits/LANE-X-R31A-R9K-R2_PREFIX_WINDOW_TOP_LEVEL_STRICT_CANDIDATE_PROPAGATION_PATCH_NO_REPLAY_NO_ORDER_retry_top_level_candidate_propagation_smoke_with_real_r9i_prefix_window_preserving_state_20260607_194326_smoke.log`

Patch doctrine:
- promotes only already-strict nested family candidates
- smoke uses real R9I prefix window so state is preserved
- no replay/order/risk/execution start
