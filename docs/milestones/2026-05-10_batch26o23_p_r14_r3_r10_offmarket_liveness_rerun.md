# 2026-05-10 — 26-O23-P-R14-R3-R10

Verdict: `FAIL_O23_P_R14_R3_R10_OFFMARKET_READONLY_LIVENESS_NOT_PROVEN`

## Off-market service liveness
- services_started: `['feeds', 'features', 'strategy']`
- alive_seen_by_service: `{'feeds': False, 'features': False, 'strategy': False}`
- service_liveness_observed: `False`
- token_bootstrap_error_seen: `False`
- features_growth: `0`
- decisions_growth: `0`
- payload_status: `PAYLOAD_LIVE_SESSION_DEFERRED_NO_OFFMARKET_STREAM_PROOF`

## Safety
- orders_growth: `0`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids_after_stop: `True`
- risk_execution_not_running: `True`

Next: 26-O23-P-R14-R4 live-session read-only R13 decision payload verification; require fresh feature/decision growth and family payload keys; no paper/live.
