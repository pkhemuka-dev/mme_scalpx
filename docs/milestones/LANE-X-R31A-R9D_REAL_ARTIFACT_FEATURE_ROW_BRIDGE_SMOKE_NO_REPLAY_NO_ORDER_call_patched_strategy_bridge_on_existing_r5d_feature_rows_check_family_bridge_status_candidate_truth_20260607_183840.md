# LANE-X-R31A-R9D_REAL_ARTIFACT_FEATURE_ROW_BRIDGE_SMOKE_NO_REPLAY_NO_ORDER_call_patched_strategy_bridge_on_existing_r5d_feature_rows_check_family_bridge_status_candidate_truth_20260607_183840

classification: PASS_LANE_X_R31A_R9D_REAL_ARTIFACT_FEATURE_ROW_BRIDGE_SMOKE_OK_NO_REPLAY_NO_ORDER

- pre_safe: 1
- smoke_rc: 0
- sample_rows: 50
- adapter_invoked_count: 50
- family_non_null_count: 0
- candidate_true_count: 0
- post_orders: 0
- post_risk_stream: 0
- post_execution_stream: 0
- smoke_json: `run/audits/LANE-X-R31A-R9D_REAL_ARTIFACT_FEATURE_ROW_BRIDGE_SMOKE_NO_REPLAY_NO_ORDER_call_patched_strategy_bridge_on_existing_r5d_feature_rows_check_family_bridge_status_candidate_truth_20260607_183840_real_feature_bridge_smoke.json`
- smoke_log: `run/audits/LANE-X-R31A-R9D_REAL_ARTIFACT_FEATURE_ROW_BRIDGE_SMOKE_NO_REPLAY_NO_ORDER_call_patched_strategy_bridge_on_existing_r5d_feature_rows_check_family_bridge_status_candidate_truth_20260607_183840_real_feature_bridge_smoke.log`

Interpretation:
- If adapter_invoked_count > 0 but family_non_null_count = 0, R9B wrapper works but feature rows still lack family truth.
- If family_non_null_count > 0, proceed to tiny replay smoke.
- candidate_true_count must not be treated as profitability proof.

Boundary: no replay, no order, no paper/live, no risk/execution, no threshold tuning, no candidate forcing.
