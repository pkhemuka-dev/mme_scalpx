# LANE-X-R31A-R9F-R5_RAW_DECISION_SHAPE_DUMP_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_strategy_adapter_output_shape_after_r9b_r9f_r1_before_sanitizer_retry_20260607_185634

classification: PASS_LANE_X_R31A_R9F_R5_RAW_DECISION_SHAPE_DUMP_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- first_frame_family_features_present: 1
- candidate_path_count: 8
- r9b_marker_count: 1
- r9f_r1_marker_count: 1
- r9f_r3_marker_count: 0
- output_json: `run/audits/LANE-X-R31A-R9F-R5_RAW_DECISION_SHAPE_DUMP_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_strategy_adapter_output_shape_after_r9b_r9f_r1_before_sanitizer_retry_20260607_185634_raw_decision_shape.json`
- output_text: `run/audits/LANE-X-R31A-R9F-R5_RAW_DECISION_SHAPE_DUMP_NO_PATCH_NO_REPLAY_NO_ORDER_dump_exact_strategy_adapter_output_shape_after_r9b_r9f_r1_before_sanitizer_retry_20260607_185634_raw_decision_shape.txt`

Decision:
- If candidate_path_count > 0, patch exact path.
- If candidate_path_count = 0 but family features present, adapter is returning no candidate report in this shape; run adapter direct-shape audit.

Boundary: no patch, no replay, no order.
