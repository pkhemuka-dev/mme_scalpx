# LANE-X-R31A-R9Q-R2_COMPACT_ROW168_R9I_R9L_TRUTH_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_compact_compare_row168_r9i_r9l_feature_surface_candidate_truth_without_large_json_flood_20260607_204018

classification: PASS_LANE_X_R31A_R9Q_R2_COMPACT_ROW168_DIFF_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- r9i_feature_breakout_true: 1
- r9l_feature_breakout_true: 1
- r9i_strategy_strict_count: 3
- r9l_strategy_strict_count: 0
- output_json: `run/audits/LANE-X-R31A-R9Q-R2_COMPACT_ROW168_R9I_R9L_TRUTH_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_compact_compare_row168_r9i_r9l_feature_surface_candidate_truth_without_large_json_flood_20260607_204018_compact_row168_diff.json`
- output_text: `run/audits/LANE-X-R31A-R9Q-R2_COMPACT_ROW168_R9I_R9L_TRUTH_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_compact_compare_row168_r9i_r9l_feature_surface_candidate_truth_without_large_json_flood_20260607_204018_compact_row168_diff.txt`

Decision:
- If R9I feature breakout=true but R9L feature breakout=false, replay feature reconstruction is nondeterministic or source changed.
- If both feature breakouts true but R9L strategy strict=0, adapter/bridge truth is the seam.
- If R9L strict>0 but top remains HOLD, propagation placement is the seam.

Boundary: no patch, no replay, no order.
