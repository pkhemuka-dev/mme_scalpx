# 2026-05-10 — 26-O23-P-R14-R3-R11

Verdict: `FAIL_O23_P_R14_R3_R11_OFFMARKET_READONLY_SERVICE_START_NOT_PROVEN`

## Off-market service start
- services_started: `['feeds', 'features', 'strategy']`
- service_liveness_observed: `False`
- service_exit_classification: `POST_PATCH_SERVICE_EXIT_WITH_SEVERE_LOG`
- token_bootstrap_error_seen: `False`
- quote_shape_error_seen: `False`
- severe_error_seen: `True`
- payload_status: `PAYLOAD_DEFERRED_SERVICE_SEVERE_LOG_REMAINS`

## Safety
- orders_growth: `0`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids_after_stop: `True`
- risk_execution_not_running: `True`

Next: 26-O23-P-R14-R3-R11-R2 classify remaining severe service-start log after quote-shape patch; no paper/live.
