# LANE-MIV-R4-R3_AFTERMARKET_PERCENT_READINESS_FINALIZER_NO_PATCH_NO_REPLAY_NO_ORDER_freeze_r4r2_measurement_pipeline_pass_and_tomorrow_percent_result_checklist_20260611_235103 Runbook

Tomorrow:
1. Keep observe-only capture running.
2. Do not enable paper/live.
3. Do not start risk/execution service.
4. After close, run R4-R1 locator on latest durable_capture.
5. Run R4-R2 compact measurement builder.
6. Report:
   - candidate count
   - candidate_intent count
   - risk_shadow count
   - execution_sim fill count
   - order_intent_ledger count
   - win %
   - avg return %
   - net shadow PnL %
   - CALL/PUT breakdown
7. If candidate count remains high, add rank/bucket throttle to 20-40/day only after measurement.
