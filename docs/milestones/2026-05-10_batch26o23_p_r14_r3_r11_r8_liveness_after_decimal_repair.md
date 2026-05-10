# 2026-05-10 — 26-O23-P-R14-R3-R11-R8

Verdict: `FAIL_O23_P_R14_R3_R11_R8_DECIMAL_REPAIR_SERVICE_START_NOT_PROVEN`

## Off-market service start
- selected_ltp: `22350.0`
- selected_source: `artifact:run/replay/guarded_offline/batch30j_r5aj_same_dataset_repeatability_20260417_20260510_101415_run_a/replay_locked_single_day_20260510_044415_11a896df/artifacts/features_rows.json`
- services_started: `['feeds', 'features', 'strategy']`
- service_liveness_observed: `True`
- service_exit_classification: `SERVICE_LIVENESS_OBSERVED`
- token_bootstrap_error_seen: `False`
- instrument_validation_error_seen: `False`
- decimal_float_error_seen: `False`
- severe_error_seen: `True`
- payload_status: `PAYLOAD_VERIFIED_EVEN_OFF_MARKET`

## Safety
- orders_growth: `0`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids_after_stop: `True`
- risk_execution_not_running: `True`

Next: 26-O23-Q-R2 rerun family surface materialization/payload inspection and rank only evidence-backed family/side surfaces; no paper/live.
