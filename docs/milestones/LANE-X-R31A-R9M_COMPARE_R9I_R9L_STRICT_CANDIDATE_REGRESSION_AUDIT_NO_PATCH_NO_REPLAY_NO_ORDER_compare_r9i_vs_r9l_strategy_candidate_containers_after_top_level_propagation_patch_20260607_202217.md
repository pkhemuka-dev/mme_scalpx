# LANE-X-R31A-R9M_COMPARE_R9I_R9L_STRICT_CANDIDATE_REGRESSION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_compare_r9i_vs_r9l_strategy_candidate_containers_after_top_level_propagation_patch_20260607_202217

classification: PASS_LANE_X_R31A_R9M_R9I_R9L_STRICT_CANDIDATE_REGRESSION_AUDIT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- r9i_strict_total: 633
- r9l_strict_total: 0
- r9l_candidate_container_rows: 11789
- output_json: `run/audits/LANE-X-R31A-R9M_COMPARE_R9I_R9L_STRICT_CANDIDATE_REGRESSION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_compare_r9i_vs_r9l_strategy_candidate_containers_after_top_level_propagation_patch_20260607_202217_r9i_r9l_compare.json`
- output_text: `run/audits/LANE-X-R31A-R9M_COMPARE_R9I_R9L_STRICT_CANDIDATE_REGRESSION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_compare_r9i_vs_r9l_strategy_candidate_containers_after_top_level_propagation_patch_20260607_202217_r9i_r9l_compare.txt`

Decision:
- If R9L candidate containers exist but candidate_present/eligible changed, patch candidate truth interaction.
- If R9L candidate containers are gone/empty, R9K-R6 disrupted adapter payload path or matched wrong branch.
- No PnL claim until candidate reaches risk/execution shadow.

Boundary: no patch, no replay, no order.
