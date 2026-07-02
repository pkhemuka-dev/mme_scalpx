# LANE-X-R19D_pfeedcheck_zerodha_growth_helper_patch_no_order_20260604_205936

classification: PASS_LANE_X_R19D_PFEEDCHECK_ZERODHA_GROWTH_HELPER_PATCH_OK_NO_ORDER

Patched helper-only pfeedcheck growth variables.

## Change

- Added explicit zerodha_critical_growth.
- Added explicit dhan_critical_growth.
- Set classic critical_growth to Zerodha futures + Zerodha selected option growth.
- Added degraded note when Zerodha is healthy but Dhan is incomplete.
- Preserved MISO fail-closed doctrine; this helper patch does not enable MISO.

No production Python, paper, broker/order, risk, or execution path was touched.
