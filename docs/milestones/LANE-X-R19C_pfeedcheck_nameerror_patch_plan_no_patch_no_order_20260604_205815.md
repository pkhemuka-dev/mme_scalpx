# LANE-X-R19C_pfeedcheck_nameerror_patch_plan_no_patch_no_order_20260604_205815

classification: PASS_LANE_X_R19C_PFEEDCHECK_NAMEERROR_PATCH_PLAN_READY_NO_PATCH_NO_ORDER

pfeedcheck helper bug patch plan prepared. No patch was applied.

The intended fix is shell-helper-only: define zerodha_critical_growth and dhan_critical_growth explicitly in the active pfeedcheck logic, while preserving Dhan/MISO fail-closed doctrine.

No production Python, paper, broker/order, risk, or execution path was touched.
