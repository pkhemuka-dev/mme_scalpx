# 2026-05-10 — 26-O23-P-R14-R3-R5

Verdict: `FAIL_O23_P_R14_R3_R5_SERVICE_EXIT_CLASSIFIER_NOT_PROVEN`

## Classification
- classification: `R14_R3_R4_SERVICES_LAUNCHED_BUT_EXITED_WITH_LOG_ERRORS`
- all_three_launched: `True`
- only_liveness_false: `True`
- any_severe_log_error: `True`
- nonzero_returncodes: `{'feeds': 1, 'features': 1, 'strategy': 1}`

## Safety
- source_patch_applied: `False`
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- risk_execution_not_running: `True`

Next: Inspect R14-R3-R5 service log classification; repair exact service startup error only; no paper/live.
