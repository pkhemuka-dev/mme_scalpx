# LANE-X-R31A-R9K-R3_FEATURE_STRATEGY_PARITY_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_compare_r9i_saved_feature_rows_vs_strategy_rows_around_strict_nested_candidates_before_top_level_patch_retry_20260607_194452

classification: PASS_LANE_X_R31A_R9K_R3_FEATURE_STRATEGY_PARITY_AUDIT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- strict_strategy_row_count: 211
- strict_candidate_total_estimate: 633
- output_json: `run/audits/LANE-X-R31A-R9K-R3_FEATURE_STRATEGY_PARITY_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_compare_r9i_saved_feature_rows_vs_strategy_rows_around_strict_nested_candidates_before_top_level_patch_retry_20260607_194452_parity_audit.json`
- output_text: `run/audits/LANE-X-R31A-R9K-R3_FEATURE_STRATEGY_PARITY_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_compare_r9i_saved_feature_rows_vs_strategy_rows_around_strict_nested_candidates_before_top_level_patch_retry_20260607_194452_parity_audit.txt`

Decision:
- If strict rows are present only in saved strategy_decisions, patch propagation near serialization/export path or rerun replay with propagation active.
- If matching feature rows lack the values that produced strict candidates, patch export parity, not strategy logic.
- No PnL claim until top-level candidate reaches risk/execution shadow.

Boundary: no patch, no replay, no order.
