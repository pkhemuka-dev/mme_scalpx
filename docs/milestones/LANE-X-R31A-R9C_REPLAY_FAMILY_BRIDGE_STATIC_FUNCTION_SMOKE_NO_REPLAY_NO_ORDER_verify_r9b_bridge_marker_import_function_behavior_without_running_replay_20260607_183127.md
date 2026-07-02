# LANE-X-R31A-R9C_REPLAY_FAMILY_BRIDGE_STATIC_FUNCTION_SMOKE_NO_REPLAY_NO_ORDER_verify_r9b_bridge_marker_import_function_behavior_without_running_replay_20260607_183127

classification: REVIEW_LANE_X_R31A_R9C_STATIC_FUNCTION_SMOKE_FAILED_NO_REPLAY_NO_ORDER

- compile_rc: 0
- smoke_rc: 1
- marker_count: 1
- wrapper_count: 1
- fallback_count: 1
- bridge_status_seen: 0
0
- pre_replay_proc: 0
- post_orders: 0
- post_risk_stream: 0
- post_execution_stream: 0
- smoke_log: `run/audits/LANE-X-R31A-R9C_REPLAY_FAMILY_BRIDGE_STATIC_FUNCTION_SMOKE_NO_REPLAY_NO_ORDER_verify_r9b_bridge_marker_import_function_behavior_without_running_replay_20260607_183127_smoke.log`

Interpretation:
- This proves the R9B bridge can import and execute on a synthetic frame.
- It does not prove family candidates or PnL.
- If PASS, next is a tiny replay smoke with existing data, no order.

Boundary: no replay, no order, no paper/live, no risk/execution, no threshold tuning, no candidate forcing.
