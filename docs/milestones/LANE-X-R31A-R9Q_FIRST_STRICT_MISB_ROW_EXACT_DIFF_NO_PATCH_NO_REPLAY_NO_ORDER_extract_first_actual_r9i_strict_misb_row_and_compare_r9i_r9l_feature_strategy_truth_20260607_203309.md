# LANE-X-R31A-R9Q_FIRST_STRICT_MISB_ROW_EXACT_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_extract_first_actual_r9i_strict_misb_row_and_compare_r9i_r9l_feature_strategy_truth_20260607_203309

classification: PASS_LANE_X_R31A_R9Q_FIRST_STRICT_MISB_ROW_EXACT_DIFF_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- strict_misb_index_count: 211
- first_strict_misb_index: 168
- output_json: `run/audits/LANE-X-R31A-R9Q_FIRST_STRICT_MISB_ROW_EXACT_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_extract_first_actual_r9i_strict_misb_row_and_compare_r9i_r9l_feature_strategy_truth_20260607_203309_first_strict_misb_exact_diff.json`
- output_text: `run/audits/LANE-X-R31A-R9Q_FIRST_STRICT_MISB_ROW_EXACT_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_extract_first_actual_r9i_strict_misb_row_and_compare_r9i_r9l_feature_strategy_truth_20260607_203309_first_strict_misb_exact_diff.txt`

Decision:
- If first strict R9I feature has breakout=true but R9L feature has breakout=false, feature enrichment/replay determinism is the seam.
- If features match but strategy candidates differ, strategy_adapter or candidate truth serialization is the seam.
- If R9L strategy candidate is strict but top remains HOLD, propagation placement is the seam.

Boundary: no patch, no replay, no order.
