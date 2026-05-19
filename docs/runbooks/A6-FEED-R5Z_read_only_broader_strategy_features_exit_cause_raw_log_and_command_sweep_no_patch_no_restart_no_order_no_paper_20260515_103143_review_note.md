# A6-FEED-R5Z_read_only_broader_strategy_features_exit_cause_raw_log_and_command_sweep_no_patch_no_restart_no_order_no_paper_20260515_103143 Review Note

Batch: A6-FEED-R5Z

Verdict: PASS_A6_FEED_R5Z_HIGH_SIGNAL_EXIT_LOGS_CAPTURED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: no patch, no restore, no start/restart/stop, no Redis write, no paper/live, no broker/order, no risk/execution.

Classification:

```json
{
  "decisions_stream_age_ms": 2325255,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 846667,
  "features_stream_xlen": 91,
  "high_signal_log_count": 15,
  "likely_condition": "NO_REAL_NAMEERROR_FOUND_BUT_HIGH_SIGNAL_EXIT_OR_GATE_LOGS_CAPTURED",
  "log_path_count": 17,
  "next_action": "Review high-signal logs. Next should classify actual exit/gate signature, not NameError. No patch yet unless exact source cause is clear.",
  "r5w_final_verdict": "PASS_A6_FEED_R5W_STRATEGY_FEATURES_EXIT_CAUSE_EVIDENCE_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5w_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5W_read_only_strategy_features_start_log_exit_cause_inspection_after_services_not_running_no_patch_no_restart_no_order_no_paper_20260515_102207.json",
  "r5y_r2_final_verdict": "BLOCKED_A6_FEED_R5Y_R2_EXACT_NAMEERROR_EXTRACTION_INCOMPLETE_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5y_r2_likely_condition": "RAW_LOGS_FOUND_BUT_NO_VALID_IDENTIFIER_NAMEERROR_EXTRACTED",
  "r5y_r2_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Y-R2_corrected_read_only_extract_exact_strategy_nameerror_from_raw_logs_fixed_identifier_regex_no_patch_no_restart_no_order_no_paper_20260515_102934.json",
  "real_nameerror_symbols": [],
  "standard_services": []
}
```

High-signal log summary:

```json
[
  {
    "error_hit_count": 26,
    "has_exception_word": false,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-15T04:57:31.872341+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Y_read_only_extract_exact_strategy_nameerror_and_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_102730.json",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 1,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-15T04:55:21.239145+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5X_read_only_classify_strategy_features_exit_log_findings_before_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_102508.json",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 3,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-15T04:52:26.158140+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5W_read_only_strategy_features_start_log_exit_cause_inspection_after_services_not_running_no_patch_no_restart_no_order_no_paper_20260515_102207.json",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 234,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": true,
    "mtime_iso_utc": "2026-05-15T04:49:08.265180+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5V_read_only_strategy_log_and_feature_consumer_gate_inspection_after_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_101833.json",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 5,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": false,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-15T04:47:53.901807+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236.features.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 163,
    "has_exception_word": false,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": true,
    "mtime_iso_utc": "2026-05-15T04:47:48.150314+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101236.strategy.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 28,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-15T04:44:51.784199+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101356.json",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 14,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-15T04:38:58.498922+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5T_read_only_execute_verified_pstackcheck_strategy_status_no_start_no_order_no_paper_20260515_100831.json",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 2,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": true,
    "mtime_iso_utc": "2026-05-13T04:02:06.767587+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/pstrategy_20260513_093158.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 2,
    "has_exception_word": true,
    "has_exit_word": true,
    "has_lock_word": true,
    "has_traceback": true,
    "mtime_iso_utc": "2026-05-13T04:01:58.619846+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/pfeatures_20260513_093158.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 1,
    "has_exception_word": true,
    "has_exit_word": false,
    "has_lock_word": false,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-13T02:24:28.012913+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5G-R2_approved_observe_only_stack_recovery_after_r5g_shell_expansion_abort_no_order_no_broker_20260513_075338_strategy.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 1,
    "has_exception_word": true,
    "has_exit_word": false,
    "has_lock_word": false,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-13T02:24:20.002185+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5G-R2_approved_observe_only_stack_recovery_after_r5g_shell_expansion_abort_no_order_no_broker_20260513_075338_features.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 1,
    "has_exception_word": true,
    "has_exit_word": false,
    "has_lock_word": false,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-13T02:10:26.938450+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011_strategy.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 1,
    "has_exception_word": true,
    "has_exit_word": false,
    "has_lock_word": false,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-13T02:10:21.977998+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011_features.log",
    "real_nameerror_symbols": []
  },
  {
    "error_hit_count": 4,
    "has_exception_word": false,
    "has_exit_word": false,
    "has_lock_word": true,
    "has_traceback": false,
    "mtime_iso_utc": "2026-05-13T02:10:17.575598+00:00",
    "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/logs/A6-FEED-R5F_approved_observe_only_features_strategy_reload_after_provider_mapping_patch_no_order_no_broker_20260513_074011.log",
    "real_nameerror_symbols": []
  }
]
```

Next rule:
- Do not patch from R5X/R5Y NameError unless a real valid identifier appears in raw logs.
- If high-signal logs show a different exit/gate issue, classify that actual issue first.
- If logs are unclear, inspect command/start path and process lifetime read-only before another start attempt.
