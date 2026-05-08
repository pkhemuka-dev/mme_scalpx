# 26-O23-P-R2 — pre-existing MME PID / failed O23-P service-audit cleanup

- generated_at_utc: `2026-05-08T06:25:53.144572+00:00`
- final_verdict: `FAIL_O23_P_R2_PREEXISTING_PID_CLEANUP_NOT_PROVEN`
- false_keys: `['latest_o23_p_orders_no_growth', 'manifest_written', 'milestone_written', 'proof_written', 'runbook_written', 'summary_written']`
- latest_o23_p_proof: `run/proofs/proof_batch26o23_p_readonly_service_liveness_output_latest.json`
- latest_o23_p_false_keys: `['pre_existing_mme_pids_zero', 'runtime_no_mme_service_pids_after_stop', 'service_liveness_observed', 'service_start_allowed', 'started_feeds_features_strategy_only']`
- pre_cleanup_mme_pid_count: `1`
- post_cleanup_mme_pid_count: `0`
- cleanup_blocked: `False`
- cleanup_reason: `pre_existing_cleanable_mme_pids_terminated`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`
- no service start / no paper / no real-live / no broker call / no order write / no source patch: `True`
- next_recommended_batch: `Inspect PID audit and false_keys; do not rerun O23-P until MME PID state is clean.`

## Artifacts
- proof: `run/proofs/proof_batch26o23_p_r2_pid_service_audit_cleanup.json`
- latest_proof: `run/proofs/proof_batch26o23_p_r2_pid_service_audit_cleanup_latest.json`
- manifest: `run/live_capture/batch26o23_p_r2_pid_service_audit_cleanup_20260508_115553/manifest_batch26o23_p_r2_pid_service_audit_cleanup.json`
- failed_p_audit: `run/live_capture/batch26o23_p_r2_pid_service_audit_cleanup_20260508_115553/o23p_r2_failed_p_artifact_audit.json`
- pid_audit: `run/live_capture/batch26o23_p_r2_pid_service_audit_cleanup_20260508_115553/o23p_r2_current_pid_audit.json`
- cleanup: `run/live_capture/batch26o23_p_r2_pid_service_audit_cleanup_20260508_115553/o23p_r2_pid_cleanup_actions.json`
- safety: `run/live_capture/batch26o23_p_r2_pid_service_audit_cleanup_20260508_115553/o23p_r2_runtime_safety_readback.json`
