# LANE-X-R31A-R9N_R9I_R9L_ROW168_CANDIDATE_FIELD_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_exact_candidate_truth_field_regression_after_r9k_r6_patch_20260607_202423

classification: PASS_LANE_X_R31A_R9N_ROW168_CANDIDATE_FIELD_DIFF_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- output_json: `run/audits/LANE-X-R31A-R9N_R9I_R9L_ROW168_CANDIDATE_FIELD_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_exact_candidate_truth_field_regression_after_r9k_r6_patch_20260607_202423_row168_diff.json`
- output_text: `run/audits/LANE-X-R31A-R9N_R9I_R9L_ROW168_CANDIDATE_FIELD_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_exact_candidate_truth_field_regression_after_r9k_r6_patch_20260607_202423_row168_diff.txt`

Decision:
- If R9L nested MISB candidates are present but eligible=false or blockers reappear, inspect R9K-R6 interaction with candidate truth.
- If R9L nested candidates are present and strict, but top remains HOLD, patch propagation placement.
- If R9L MISB surfaces lost breakout fields, patch feature enrichment/export ordering.

Boundary: no patch, no replay, no order.
