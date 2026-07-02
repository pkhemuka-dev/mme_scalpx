# LANE-X-R31A-R9O_CANDIDATE_TRUTH_INTERACTION_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_r9f_r8_r9k_r6_candidate_truth_assignment_order_after_r9l_strict_regression_20260607_202714

classification: PASS_LANE_X_R31A_R9O_CANDIDATE_TRUTH_INTERACTION_SOURCE_AUDIT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- r9k_r6_marker_count: 1
- r9f_r8_marker_count: 1
- candidate_present_assignment_count: 8
- strict_candidate_count_assignment_count: 1
- output: `run/audits/LANE-X-R31A-R9O_CANDIDATE_TRUTH_INTERACTION_SOURCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_audit_r9f_r8_r9k_r6_candidate_truth_assignment_order_after_r9l_strict_regression_20260607_202714_source_truth_interaction.txt`

Decision:
- If R9K-R6 has an else/default that sets candidate false before final adapter truth, move propagation later.
- If R9F-R8 truth is correct but R9L recomputed surfaces are weaker, inspect the exact R9L row where MISB breakout changed.
- Do not patch until this source interaction is read.

Boundary: no patch, no replay, no order.
