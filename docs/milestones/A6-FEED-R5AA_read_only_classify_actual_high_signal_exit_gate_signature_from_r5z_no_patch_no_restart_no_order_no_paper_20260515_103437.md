# A6-FEED-R5AA_read_only_classify_actual_high_signal_exit_gate_signature_from_r5z_no_patch_no_restart_no_order_no_paper_20260515_103437

Batch: A6-FEED-R5AA

Purpose: read_only_classify_actual_high_signal_exit_gate_signature_from_r5z_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5AA_ACTUAL_HIGH_SIGNAL_EXIT_GATE_SIGNATURE_CLASSIFIED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only high-signal exit/gate classification only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "decisions_stream_age_ms": 2498724,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 1020138,
  "features_stream_xlen": 91,
  "important_window_count": 80,
  "likely_condition": "SERVICE_COMMAND_SHAPE_OR_ARGPARSE_MISMATCH",
  "next_action": "Prepare read-only command-shape comparison or narrow patch plan only if main.py CLI contract is clearly wrong. No restart/paper/live.",
  "r5z_final_verdict": "PASS_A6_FEED_R5Z_HIGH_SIGNAL_EXIT_LOGS_CAPTURED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5z_likely_condition": "NO_REAL_NAMEERROR_FOUND_BUT_HIGH_SIGNAL_EXIT_OR_GATE_LOGS_CAPTURED",
  "r5z_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5Z_read_only_broader_strategy_features_exit_cause_raw_log_and_command_sweep_no_patch_no_restart_no_order_no_paper_20260515_103143.json",
  "signature_scores": {
    "argparse_unrecognized_argument": 13,
    "attribute_error": 0,
    "consumer_group_issue": 1,
    "decision_publish_gate": 179,
    "empty_or_missing_input": 88,
    "feature_consumer_gate": 46,
    "import_error": 0,
    "key_error": 0,
    "lock_or_singleton": 166,
    "main_service_command_shape": 28,
    "normal_exit_or_shutdown": 18,
    "permission_or_path": 0,
    "provider_context_gate": 184,
    "traceback": 169,
    "type_error": 0,
    "valid_name_error": 0,
    "value_error": 0
  },
  "standard_services": []
}
```

Signature scores:

```json
{
  "argparse_unrecognized_argument": 13,
  "attribute_error": 0,
  "consumer_group_issue": 1,
  "decision_publish_gate": 179,
  "empty_or_missing_input": 88,
  "feature_consumer_gate": 46,
  "import_error": 0,
  "key_error": 0,
  "lock_or_singleton": 166,
  "main_service_command_shape": 28,
  "normal_exit_or_shutdown": 18,
  "permission_or_path": 0,
  "provider_context_gate": 184,
  "traceback": 169,
  "type_error": 0,
  "valid_name_error": 0,
  "value_error": 0
}
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5z_proof_found": true,
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
  "r5z_high_signal_logs_captured": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AA_read_only_classify_actual_high_signal_exit_gate_signature_from_r5z_no_patch_no_restart_no_order_no_paper_20260515_103437.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AA_read_only_classify_actual_high_signal_exit_gate_signature_from_r5z_no_patch_no_restart_no_order_no_paper_20260515_103437_classification_note.md
