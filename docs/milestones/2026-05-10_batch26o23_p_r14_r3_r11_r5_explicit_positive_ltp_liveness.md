# 2026-05-10 — 26-O23-P-R14-R3-R11-R5

Verdict: `FAIL_O23_P_R14_R3_R11_R5_POSITIVE_FALLBACK_SERVICE_START_NOT_PROVEN`

## Off-market service start
- fallback_ltp: `None`
- fallback_ltp_source: `None`
- services_started: `[]`
- service_liveness_observed: `False`
- service_exit_classification: `OFFMARKET_SERVICE_EXIT_UNCLASSIFIED`
- token_bootstrap_error_seen: `False`
- instrument_validation_error_seen: `False`
- severe_error_seen: `False`
- payload_status: `PAYLOAD_DEFERRED_SERVICE_START_REFUSED_NO_POSITIVE_FALLBACK`

## Safety
- orders_growth: `0`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids_after_stop: `True`
- risk_execution_not_running: `True`

Next: Provide explicit positive SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK from known safe read-only observed NIFTY LTP, then rerun 26-O23-P-R14-R3-R11-R5; no paper/live.
