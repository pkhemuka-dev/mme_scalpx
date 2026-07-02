# LANE-X-DASH-R3E_REFINE_NEXT_ACTION_FRESH_ERROR_ONLY_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER

Classification: **PASS_LANE_X_DASH_R3E_NEXT_ACTION_FRESH_ERROR_ONLY_PATCHED_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER**

Refined dashboard NEXT ACTION logic.

Old logic:

`errors_len > 0 => REVIEW_ERRORS`

New logic:

`fresh_error age <= 180 sec => REVIEW_ERRORS`

Historical errors no longer override the more useful Lane X next action.

Checks:
- compile_ok=1
- import_ok=1
- ast_readonly_ok=1
- markers_ok=1
- safety_ok=1

Safety:
- orders_before=0
- orders_after=0
- risk_stream_after=0
- execution_stream_after=0
- risk_proc_after=0
- execution_proc_after=0
