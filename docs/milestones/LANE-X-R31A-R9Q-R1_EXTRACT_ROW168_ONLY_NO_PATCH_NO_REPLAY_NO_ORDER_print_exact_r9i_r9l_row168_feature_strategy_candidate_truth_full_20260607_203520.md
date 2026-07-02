# LANE-X-R31A-R9Q-R1_EXTRACT_ROW168_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_print_exact_r9i_r9l_row168_feature_strategy_candidate_truth_full_20260607_203520

classification: PASS_LANE_X_R31A_R9Q_R1_ROW168_EXTRACT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- source_json: `run/audits/LANE-X-R31A-R9Q_FIRST_STRICT_MISB_ROW_EXACT_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_extract_first_actual_r9i_strict_misb_row_and_compare_r9i_r9l_feature_strategy_truth_20260607_203309_first_strict_misb_exact_diff.json`
- output_json: `run/audits/LANE-X-R31A-R9Q-R1_EXTRACT_ROW168_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_print_exact_r9i_r9l_row168_feature_strategy_candidate_truth_full_20260607_203520_row168_only.json`
- output_text: `run/audits/LANE-X-R31A-R9Q-R1_EXTRACT_ROW168_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_print_exact_r9i_r9l_row168_feature_strategy_candidate_truth_full_20260607_203520_row168_only.txt`

Decision:
- If R9I row 168 feature has breakout=true and R9L row 168 feature has breakout=false, feature/replay determinism changed.
- If features match but R9I/R9L strategy candidates differ, adapter/bridge truth changed.
- If R9L strategy candidate is strict but top remains HOLD, propagation placement is still wrong.

Boundary: no patch, no replay, no order.
