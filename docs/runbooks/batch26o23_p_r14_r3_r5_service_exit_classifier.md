# 26-O23-P-R14-R3-R5 — service exit / liveness miss classifier

- generated_at_utc: `2026-05-10T04:18:22.352905+00:00`
- final_verdict: `FAIL_O23_P_R14_R3_R5_SERVICE_EXIT_CLASSIFIER_NOT_PROVEN`
- false_keys: `['manifest_written', 'milestone_written', 'proof_written', 'runbook_written']`
- classification: `R14_R3_R4_SERVICES_LAUNCHED_BUT_EXITED_WITH_LOG_ERRORS`
- classification_supported: `True`
- all_three_launched: `True`
- only_liveness_false: `True`
- any_severe_log_error: `True`
- nonzero_returncodes: `{'feeds': 1, 'features': 1, 'strategy': 1}`
- source_patch_applied: `False`
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`
- next_recommended_batch: `Inspect R14-R3-R5 service log classification; repair exact service startup error only; no paper/live.`
