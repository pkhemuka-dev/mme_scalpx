# A6-FEED-R5Z_read_only_broader_strategy_features_exit_cause_raw_log_and_command_sweep_no_patch_no_restart_no_order_no_paper_20260515_103143

Batch: A6-FEED-R5Z

Purpose: read_only_broader_strategy_features_exit_cause_raw_log_and_command_sweep_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5Z_HIGH_SIGNAL_EXIT_LOGS_CAPTURED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only broader raw-log and command-shape sweep only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

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

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5w_proof_found": true,
  "latest_r5y_r2_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "r5y_r2_no_valid_nameerror_identifier": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Z_read_only_broader_strategy_features_exit_cause_raw_log_and_command_sweep_no_patch_no_restart_no_order_no_paper_20260515_103143.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5Z_read_only_broader_strategy_features_exit_cause_raw_log_and_command_sweep_no_patch_no_restart_no_order_no_paper_20260515_103143_review_note.md
