# LANE-MIV-R4_AFTERMARKET_MEASUREMENT_PIPELINE_NO_SOURCE_PATCH_NO_REPLAY_NO_ORDER_generate_miv_candidates_internal_ledgers_shadow_percent_readiness_for_tomorrow_observe_only_result_20260611_234406 Runbook

Tomorrow observe-only goal:

1. Keep capture running observe-only.
2. After close, rerun this same measurement path on the latest durable_capture.
3. Report:
   - MIV candidate count
   - candidate_intent count
   - risk_shadow count
   - execution_sim fill count
   - order_intent_ledger count
   - win %
   - avg return %
   - net shadow PnL %
   - CALL/PUT breakdown

Never:
- send broker order
- enable paper/live
- start risk/execution services
- delete Redis
- delete locks
