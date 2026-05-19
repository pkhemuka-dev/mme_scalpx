# A6-FEED-R5AI-R2_clipboard_safe_distill_exact_non_frame_error_gate_signature_from_r5ah_raw_windows_no_patch_no_restart_no_order_no_paper_20260515_105722

Batch: A6-FEED-R5AI-R2

Purpose: clipboard_safe_distill_exact_non_frame_error_gate_signature_from_r5ah_raw_windows_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5AI_R2_EXACT_RAW_SIGNATURES_DISTILLED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only exact non-frame raw signature distillation only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "category_counts": {
    "argparse_or_command": 22,
    "consumer_group": 1,
    "decision_publish": 194,
    "feature_consumer": 280,
    "generic_error": 87,
    "normal_exit_shutdown": 84,
    "provider_context": 74,
    "stale_missing_invalid": 353,
    "traceback_word_no_python_frames": 472,
    "uncategorized": 1795
  },
  "decisions_stream_age_ms": 3854939,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 570616,
  "features_stream_xlen": 131,
  "likely_condition": "RAW_SIGNATURE_POINTS_TO_CONSUMER_GROUP_GATE",
  "next_action": "Inspect Redis XINFO GROUPS/CONSUMERS read-only before any mutation.",
  "r5ah_combined_counts": {
    "argparse_word": 6,
    "consumer_group_word": 70,
    "decision_word": 165,
    "error_word": 1627,
    "exception_word": 22,
    "exit_word": 63,
    "failed_word": 44,
    "feature_word": 5594,
    "file_frame_word": 0,
    "lock_word": 2865,
    "stale_missing_word": 6085,
    "traceback_word": 691
  },
  "r5ah_final_verdict": "PASS_A6_FEED_R5AH_RAW_LOG_ERROR_WINDOWS_CAPTURED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ah_likely_condition": "TRACEBACK_WORD_WAS_PRESENT_WITHOUT_PYTHON_FILE_FRAMES",
  "r5ah_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AH_read_only_raw_strategy_log_error_window_extraction_after_frame_distillation_failed_no_patch_no_restart_no_order_no_paper_20260515_105451.json",
  "raw_line_count": 3362,
  "services": [],
  "top_signatures": [
    {
      "category": "traceback_word_no_python_frames",
      "count": 325,
      "normalized": "{\"exc_info\":\"Traceback (most recent call last):\\n File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 1100, in start\\n self.run_once()\\n File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 910, in run_once\\n bundle = self.bridge.read_feature_bundle()\\n File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 584, in read_feature_bundle\\n return self._bundle_from_hash(raw)\\n File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 599, in _bundle_from_hash\\n FF_C.validate_family_features_payload(family_features)\\n File \\\"/<REDACTED_SECRET_OR",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.strategy.log"
      ],
      "sample_raw": "{\"exc_info\":\"Traceback (most recent call last):\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 1100, in start\\n    self.run_once()\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 910, in run_once\\n    bundle = self.bridge.read_feature_bundle()\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 584, in read_feature_bundle\\n    return self._bundle_from_hash(raw)\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 599, in _bundle_from_hash\\n    FF_C.validate_family_features_payload(family_features)\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 2187, in validate_family_features_payload\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 1331, in validate_stage_flags_block\\n    _require_exact_keys(\\n  File \\\"/<REDACTED_SECRET_OR_TOKEN>\\\", line 658, in _require_exact_keys\\n    raise FeatureFamilyContractError(\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_vet"
    },
    {
      "category": "traceback_word_no_python_frames",
      "count": 91,
      "normalized": "\"block_redacted\": \"{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n self.run_once()\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n bundle = self.bridge.read_feature_bundle()\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n return self._bundle_from_hash(raw)\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n FF_C.validate_family_features_payload(",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json"
      ],
      "sample_raw": "\"block_redacted\": \"{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n    self.run_once()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n    bundle = self.bridge.read_feature_bundle()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n    return self._bundle_from_hash(raw)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n    FF_C.validate_family_features_payload(family_features)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 2187, in validate_family_features_payload\\\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1331, in validate_stage_flags_block\\\\n    _require_exact_keys(\\\\"
    },
    {
      "category": "uncategorized",
      "count": 80,
      "normalized": "\"log_path\": \"/<REDACTED_SECRET_OR_TOKEN>\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json"
      ],
      "sample_raw": "      \"log_path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
    },
    {
      "category": "stale_missing_invalid",
      "count": 72,
      "normalized": "\"error\": null,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json"
      ],
      "sample_raw": "\"error\": null,"
    },
    {
      "category": "stale_missing_invalid",
      "count": 65,
      "normalized": "\"exception_type\": null,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json"
      ],
      "sample_raw": "      \"exception_type\": null,"
    },
    {
      "category": "uncategorized",
      "count": 62,
      "normalized": "\"frames\": [],",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json"
      ],
      "sample_raw": "      \"frames\": [],"
    },
    {
      "category": "uncategorized",
      "count": 50,
      "normalized": "\"ok\": true",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json"
      ],
      "sample_raw": "      \"ok\": true"
    },
    {
      "category": "stale_missing_invalid",
      "count": 47,
      "normalized": "\"exception_line\": null,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json"
      ],
      "sample_raw": "      \"exception_line\": null,"
    },
    {
      "category": "stale_missing_invalid",
      "count": 47,
      "normalized": "\"exception_message\": null,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json"
      ],
      "sample_raw": "      \"exception_message\": null,"
    },
    {
      "category": "uncategorized",
      "count": 40,
      "normalized": "\"/<REDACTED_SECRET_OR_TOKEN>\": {",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json"
      ],
      "sample_raw": "    \"/<REDACTED_SECRET_OR_TOKEN>\": {"
    },
    {
      "category": "uncategorized",
      "count": 36,
      "normalized": "\"type\": \"stream\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"type\": \"stream\","
    },
    {
      "category": "feature_consumer",
      "count": 36,
      "normalized": "\"feature_payload_keys\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"feature_payload_keys\": 0,"
    },
    {
      "category": "stale_missing_invalid",
      "count": 36,
      "normalized": "\"input_gate_missing_stale\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"input_gate_missing_stale\": 0,"
    },
    {
      "category": "normal_exit_shutdown",
      "count": 36,
      "normalized": "\"normal_exit\": 3,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"normal_exit\": 3,"
    },
    {
      "category": "decision_publish",
      "count": 36,
      "normalized": "\"xadd_or_publish\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"xadd_or_publish\": 0,"
    },
    {
      "category": "uncategorized",
      "count": 34,
      "normalized": "\"latest_id\": \"<NUM>-0\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"latest_id\": \"1778822258383-0\","
    },
    {
      "category": "uncategorized",
      "count": 34,
      "normalized": "\"xread_or_group\": 0",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"xread_or_group\": 0"
    },
    {
      "category": "uncategorized",
      "count": 34,
      "normalized": "\"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"sha256\": \"<REDACTED_SECRET_OR_TOKEN>\","
    },
    {
      "category": "decision_publish",
      "count": 32,
      "normalized": "\"decision_stream\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"decision_stream\": 0,"
    },
    {
      "category": "feature_consumer",
      "count": 32,
      "normalized": "\"feature_stream\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"feature_stream\": 0,"
    },
    {
      "category": "uncategorized",
      "count": 30,
      "normalized": "\"<NUM>\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"1778822256341170865\","
    },
    {
      "category": "normal_exit_shutdown",
      "count": 30,
      "normalized": "\"exit_seen\": true,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"exit_seen\": true,"
    },
    {
      "category": "uncategorized",
      "count": 28,
      "normalized": "\"status\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"status\","
    },
    {
      "category": "uncategorized",
      "count": 28,
      "normalized": "\"detail\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"detail\","
    },
    {
      "category": "uncategorized",
      "count": 28,
      "normalized": "\"ts_ns\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"ts_ns\","
    }
  ],
  "unique_signature_count": 276
}
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5ah_proof_found": true,
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
  "r5ah_traceback_word_without_file_frames_found": true,
  "raw_lines_extracted_from_r5ah": true,
  "top_signatures_distilled": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AI-R2_clipboard_safe_distill_exact_non_frame_error_gate_signature_from_r5ah_raw_windows_no_patch_no_restart_no_order_no_paper_20260515_105722.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AI-R2_clipboard_safe_distill_exact_non_frame_error_gate_signature_from_r5ah_raw_windows_no_patch_no_restart_no_order_no_paper_20260515_105722_exact_raw_signature_note.md
