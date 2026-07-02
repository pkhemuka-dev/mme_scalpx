# LANE-X-R31A-R5_EXTRACT_R5D_SHADOW_PNL_NUMBERS_NO_PATCH_NO_REPLAY_NO_ORDER_extract_baseline_vs_shadow_trade_pnl_economics_from_completed_r5d_artifacts_20260607_154615

classification: PASS_LANE_X_R31A_R5_SHADOW_PNL_NUMBERS_EXTRACTED_NO_PATCH_NO_REPLAY_NO_ORDER

- base_exists: 1
- shadow_exists: 1
- orders: 0
- risk_stream: 0
- execution_stream: 0
- extracted_output: `run/audits/LANE-X-R31A-R5_EXTRACT_R5D_SHADOW_PNL_NUMBERS_NO_PATCH_NO_REPLAY_NO_ORDER_extract_baseline_vs_shadow_trade_pnl_economics_from_completed_r5d_artifacts_20260607_154615_extracted_shadow_pnl.txt`

Interpretation:
- This extracts existing R5D offline shadow economics only.
- This is not broker PnL, not paper PnL, not live PnL.
- If numbers are still absent or hard to parse, next step is a structured JSON parser, not new replay.

Boundary: no patch, no replay, no order, no paper/live, no risk/execution.
