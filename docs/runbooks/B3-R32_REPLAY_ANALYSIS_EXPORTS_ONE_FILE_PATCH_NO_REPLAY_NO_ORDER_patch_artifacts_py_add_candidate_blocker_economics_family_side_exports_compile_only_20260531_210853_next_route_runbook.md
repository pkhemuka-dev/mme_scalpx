# B3-R32_REPLAY_ANALYSIS_EXPORTS_ONE_FILE_PATCH_NO_REPLAY_NO_ORDER next route

Run:

`B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_ORDER_NO_RISK_EXECUTION`

Goal:

1. Run replay against existing B3-R23B slim dataset.
2. Verify new exports exist:
   - candidate_audit.csv
   - blocker_distribution.csv
   - economics_summary.json
   - family_side_summary.csv
   - b3_r32_analysis_exports_status.json
3. Verify candidate_audit rows match strategy decision rows.
4. Verify safety remains no broker/order/paper/live/risk/execution.
