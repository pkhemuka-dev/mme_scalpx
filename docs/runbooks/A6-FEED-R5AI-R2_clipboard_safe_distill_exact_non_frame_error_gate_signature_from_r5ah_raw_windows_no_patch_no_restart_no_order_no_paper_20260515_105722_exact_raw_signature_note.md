# A6-FEED-R5AI-R2_clipboard_safe_distill_exact_non_frame_error_gate_signature_from_r5ah_raw_windows_no_patch_no_restart_no_order_no_paper_20260515_105722 Exact Raw Signature Distillation

Batch: A6-FEED-R5AI-R2

Verdict: PASS_A6_FEED_R5AI_R2_EXACT_RAW_SIGNATURES_DISTILLED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only raw-signature distillation only; no patch, no restart, no Redis write, no paper/live, no broker/order, no risk/execution.

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

Top by category:

```json
{
  "argparse_or_command": [],
  "consumer_group": [],
  "decision_publish": [
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
      "category": "decision_publish",
      "count": 32,
      "normalized": "\"decision_stream\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"decision_stream\": 0,"
    },
    {
      "category": "decision_publish",
      "count": 17,
      "normalized": "\"decisions:mme:stream\": {",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "\"decisions:mme:stream\": {"
    },
    {
      "category": "decision_publish",
      "count": 13,
      "normalized": "\"decisions_stream_recent\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "\"decisions_stream_recent\","
    },
    {
      "category": "decision_publish",
      "count": 13,
      "normalized": "\"decisions_stream_grew_during_probe\"",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "    \"decisions_stream_grew_during_probe\""
    },
    {
      "category": "decision_publish",
      "count": 13,
      "normalized": "\"decisions_stream_grew_during_probe\": false,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "    \"decisions_stream_grew_during_probe\": false,"
    },
    {
      "category": "decision_publish",
      "count": 13,
      "normalized": "\"decisions_stream_present\": true,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "    \"decisions_stream_present\": true,"
    },
    {
      "category": "decision_publish",
      "count": 13,
      "normalized": "\"decisions_stream_recent\": false,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "    \"decisions_stream_recent\": false,"
    }
  ],
  "feature_consumer": [
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
      "category": "feature_consumer",
      "count": 32,
      "normalized": "\"feature_stream\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"feature_stream\": 0,"
    },
    {
      "category": "feature_consumer",
      "count": 26,
      "normalized": "\"loop_error:FeatureFamilyContractError\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"loop_error:FeatureFamilyContractError\","
    },
    {
      "category": "feature_consumer",
      "count": 25,
      "normalized": "\"features:mme:stream\": {",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json",
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "    \"features:mme:stream\": {"
    },
    {
      "category": "feature_consumer",
      "count": 20,
      "normalized": "raise FeatureFamilyContractError(\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'rec",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/logs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.strategy.log"
      ],
      "sample_raw": "raise FeatureFamilyContractError(\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present', 'snapshot_sync_valid', 'classic_provider_degraded"
    },
    {
      "category": "feature_consumer",
      "count": 13,
      "normalized": "\"key\": \"features:mme:stream\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AC-R2_clipboard_safe_freeze_minimal_supported_features_strategy_start_plan_no_start_no_order_no_paper_20260515_104057.json"
      ],
      "sample_raw": "      \"key\": \"features:mme:stream\","
    }
  ],
  "generic_error": [
    {
      "category": "generic_error",
      "count": 26,
      "normalized": "\"ERROR\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "\"ERROR\","
    },
    {
      "category": "generic_error",
      "count": 18,
      "normalized": "\"error_or_exception\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"error_or_exception\": 0,"
    },
    {
      "category": "generic_error",
      "count": 18,
      "normalized": "\"error_or_exception\": 196,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"error_or_exception\": 196,"
    }
  ],
  "normal_exit_shutdown": [
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
      "category": "normal_exit_shutdown",
      "count": 30,
      "normalized": "\"exit_seen\": true,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"exit_seen\": true,"
    }
  ],
  "provider_context": [
    {
      "category": "provider_context",
      "count": 18,
      "normalized": "\"provider_context\": 5,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"provider_context\": 5,"
    },
    {
      "category": "provider_context",
      "count": 18,
      "normalized": "\"tail_redacted\": \"{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"logging_configured level=INFO format=json\\\",\\\"process\\\":4660,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"<TIMESTAMP>\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"bootstrap_provider_not_configured\\\",\\\"process\\\":4660,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"<TIMESTAMP>\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"dependency_surfaces_resolved runtime_instruments=0 feed_ada",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"tail_redacted\": \"{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"logging_configured level=INFO format=json\\\",\\\"process\\\":4660,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T05:13:53.539048+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"bootstrap_provider_not_configured\\\",\\\"process\\\":4660,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T05:13:53.539634+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"dependency_surfaces_resolved runtime_instruments=0 feed_adapter=0 market_data_adapter=0 feed_adapters=0 zerodha_feed_adapter=0 dhan_feed_adapter=0 dhan_context_adapter=0 broker=0\\\",\\\"process\\\":4660,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T05:13:53.541641+00:00\\\"}\\n{\\\"level\\\":\\\"INFO\\\",\\\"logger\\\":\\\"app.mme_scalpx.main\\\",\\\"message\\\":\\\"consumer_group_bootstrap_completed replay=False stream_count=7\\\",\\\"process\\\":4660,\\\"thread\\\":\\\"MainThread\\\",\\\"ts\\\":\\\"2026-05-15T05:13:53.689779+00:00\\\"}\\n{\\\"level\\\":\\\"INF"
    },
    {
      "category": "provider_context",
      "count": 18,
      "normalized": "\"provider_context\": 1764,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"provider_context\": 1764,"
    }
  ],
  "stale_missing_invalid": [
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
      "category": "stale_missing_invalid",
      "count": 36,
      "normalized": "\"input_gate_missing_stale\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"input_gate_missing_stale\": 0,"
    },
    {
      "category": "stale_missing_invalid",
      "count": 12,
      "normalized": "\"after\": null,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "      \"after\": null,"
    },
    {
      "category": "stale_missing_invalid",
      "count": 12,
      "normalized": "\"before\": null,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "      \"before\": null,"
    },
    {
      "category": "stale_missing_invalid",
      "count": 12,
      "normalized": "\"delta\": null",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AD_approved_minimal_observe_only_features_strategy_start_after_plan_freeze_no_paper_no_order_no_risk_execution_20260515_104342.json"
      ],
      "sample_raw": "      \"delta\": null"
    }
  ],
  "traceback_word_no_python_frames": [
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
      "category": "traceback_word_no_python_frames",
      "count": 20,
      "normalized": "\"traceback\": 0,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"traceback\": 0,"
    },
    {
      "category": "traceback_word_no_python_frames",
      "count": 20,
      "normalized": "\"traceback\": 196,",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"traceback\": 196,"
    },
    {
      "category": "traceback_word_no_python_frames",
      "count": 16,
      "normalized": "\"tail_redacted\": \"{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n self.run_once()\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n bundle = self.bridge.read_feature_bundle()\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n return self._bundle_from_hash(raw)\\\\n File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n FF_C.validate_family_features_payload(f",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"tail_redacted\": \"{\\\"exc_info\\\":\\\"Traceback (most recent call last):\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1100, in start\\\\n    self.run_once()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 910, in run_once\\\\n    bundle = self.bridge.read_feature_bundle()\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 584, in read_feature_bundle\\\\n    return self._bundle_from_hash(raw)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 599, in _bundle_from_hash\\\\n    FF_C.validate_family_features_payload(family_features)\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 2187, in validate_family_features_payload\\\\n    validate_stage_flags_block(payload[KEY_STAGE_FLAGS])\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 1331, in validate_stage_flags_block\\\\n    _require_exact_keys(\\\\n  File \\\\\\\"/<REDACTED_SECRET_OR_TOKEN>\\\\\\\", line 658, in _require_exact_keys\\\\n    raise FeatureFamilyContractError(\\\\<REDACTED_SECRET_OR_TOKEN>: stage_flags keys mismatch. expected=('data_val"
    }
  ],
  "uncategorized": [
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
      "category": "uncategorized",
      "count": 30,
      "normalized": "\"<NUM>\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "          \"1778822256341170865\","
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
    },
    {
      "category": "uncategorized",
      "count": 28,
      "normalized": "\"path\": \"/<REDACTED_SECRET_OR_TOKEN>\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"path\": \"/<REDACTED_SECRET_OR_TOKEN>\","
    },
    {
      "category": "uncategorized",
      "count": 26,
      "normalized": "\"mtime_iso_utc\": \"<TIMESTAMP>\",",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"mtime_iso_utc\": \"2026-05-15T05:17:58.132437+00:00\","
    },
    {
      "category": "uncategorized",
      "count": 26,
      "normalized": "\"pattern_scores\": {",
      "paths": [
        "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AE_read_only_strategy_feature_consumer_decision_publish_gate_inspection_after_minimal_start_decisions_stale_no_patch_no_restart_no_order_no_paper_20260515_104725.json"
      ],
      "sample_raw": "        \"pattern_scores\": {"
    }
  ]
}
```

Next rule:
- Patch is still forbidden from this batch.
- If lock/consumer group dominates: inspect Redis state read-only first.
- If source gate dominates: inspect exact strategy source window before patch.
- A6-PAPER remains blocked.
