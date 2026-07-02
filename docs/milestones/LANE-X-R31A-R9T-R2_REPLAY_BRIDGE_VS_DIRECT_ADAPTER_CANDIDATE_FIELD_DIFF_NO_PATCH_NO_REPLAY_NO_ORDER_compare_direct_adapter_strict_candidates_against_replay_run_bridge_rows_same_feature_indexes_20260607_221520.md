# LANE-X-R31A-R9T-R2_REPLAY_BRIDGE_VS_DIRECT_ADAPTER_CANDIDATE_FIELD_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_compare_direct_adapter_strict_candidates_against_replay_run_bridge_rows_same_feature_indexes_20260607_221520

classification: PASS_LANE_X_R31A_R9T_R2_BRIDGE_DIRECT_CANDIDATE_FIELD_DIFF_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- direct_strict_total_focus: 26
- bridge_strict_total_focus: 0
- bridge_entry_rows_focus: 0
- fallback_rows: 13
- output_json: `run/audits/LANE-X-R31A-R9T-R2_REPLAY_BRIDGE_VS_DIRECT_ADAPTER_CANDIDATE_FIELD_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_compare_direct_adapter_strict_candidates_against_replay_run_bridge_rows_same_feature_indexes_20260607_221520_bridge_vs_direct_diff.json`
- output_text: `run/audits/LANE-X-R31A-R9T-R2_REPLAY_BRIDGE_VS_DIRECT_ADAPTER_CANDIDATE_FIELD_DIFF_NO_PATCH_NO_REPLAY_NO_ORDER_compare_direct_adapter_strict_candidates_against_replay_run_bridge_rows_same_feature_indexes_20260607_221520_bridge_vs_direct_diff.txt`

Decision:
- If direct_strict > 0 but bridge_strict = 0, patch replay_run bridge merge/candidate normalization.
- If both strict > 0 but top ENTRY = 0, patch top-level propagation.
- If bridge ENTRY > 0, rerun micro replay R9U.

Boundary: no patch, no replay, no order.
