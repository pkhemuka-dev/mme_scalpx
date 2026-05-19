# A6-FEED-R5AA_read_only_classify_actual_high_signal_exit_gate_signature_from_r5z_no_patch_no_restart_no_order_no_paper_20260515_103437 Classification Note

Batch: A6-FEED-R5AA

Verdict: PASS_A6_FEED_R5AA_ACTUAL_HIGH_SIGNAL_EXIT_GATE_SIGNATURE_CLASSIFIED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: no patch, no restore, no start/restart/stop, no Redis write, no paper/live, no broker/order, no risk/execution.

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

Important windows:

```json
[
  {
    "line": 3,
    "window_redacted": "[\n  {\n    \"error_hit_count\": 26,\n    \"error_hits\": [\n      {\n        \"line\": 6,\n        \"text\": \"\\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\","
  },
  {
    "line": 4,
    "window_redacted": "[\n  {\n    \"error_hit_count\": 26,\n    \"error_hits\": [\n      {\n        \"line\": 6,\n        \"text\": \"\\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\",\n        \"window_redacted\": \"  \\\"batch\\\": \\\"A6-FEED-R5Y\\\",\\n  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\""
  },
  {
    "line": 7,
    "window_redacted": "    \"error_hit_count\": 26,\n    \"error_hits\": [\n      {\n        \"line\": 6,\n        \"text\": \"\\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\",\n        \"window_redacted\": \"  \\\"batch\\\": \\\"A6-FEED-R5Y\\\",\\n  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\"\n      },\n      {\n        \"line\": 7,"
  },
  {
    "line": 8,
    "window_redacted": "    \"error_hits\": [\n      {\n        \"line\": 6,\n        \"text\": \"\\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\",\n        \"window_redacted\": \"  \\\"batch\\\": \\\"A6-FEED-R5Y\\\",\\n  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\"\n      },\n      {\n        \"line\": 7,\n        \"text\": \"\\\"nameerror\\\": {\","
  },
  {
    "line": 12,
    "window_redacted": "        \"window_redacted\": \"  \\\"batch\\\": \\\"A6-FEED-R5Y\\\",\\n  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\"\n      },\n      {\n        \"line\": 7,\n        \"text\": \"\\\"nameerror\\\": {\",\n        \"window_redacted\": \"  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\\n        \\\"\\\\n      }\\\\n    ],\\\\n    \\\": 1,\"\n      },\n      {\n        \"line\": 22,"
  },
  {
    "line": 13,
    "window_redacted": "      },\n      {\n        \"line\": 7,\n        \"text\": \"\\\"nameerror\\\": {\",\n        \"window_redacted\": \"  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\\n        \\\"\\\\n      }\\\\n    ],\\\\n    \\\": 1,\"\n      },\n      {\n        \"line\": 22,\n        \"text\": \"\\\"next_action\\\": \\\"Next: produce narrow source patch package for the exact NameError only. No restart/paper/live unless separately approved.\\\",\","
  },
  {
    "line": 17,
    "window_redacted": "        \"window_redacted\": \"  \\\"classification\\\": {\\n    \\\"context_window_count\\\": 0,\\n    \\\"frame_count\\\": 0,\\n    \\\"likely_condition\\\": \\\"EXACT_NAMEERROR_SYMBOL_AND_PATCH_SURFACE_IDENTIFIED\\\",\\n    \\\"nameerror\\\": {\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n      \\\"symbol_counts\\\": {\\n        \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\\n        \\\"\\\\n      }\\\\n    ],\\\\n    \\\": 1,\"\n      },\n      {\n        \"line\": 22,\n        \"text\": \"\\\"next_action\\\": \\\"Next: produce narrow source patch package for the exact NameError only. No restart/paper/live unless separately approved.\\\",\",\n        \"window_redacted\": \"        \\\"\\\\n      },\\\\n      {\\\\n        \\\",\\n        \\\",\\\\n  \\\"\\n      ]\\n    },\\n    \\\"next_action\\\": \\\"Next: produce narrow source patch package for the exact NameError only. No restart/paper/live unless separately approved.\\\",\\n    \\\"patch_surface\\\": {\\n      \\\"hit_files\\\": [],\\n      \\\"likely_file\\\": null,\\n      \\\"likely_pattern\\\": \\\"UNKNOWN\\\",\"\n      },\n      {\n        \"line\": 31,"
  },
  {
    "line": 18,
    "window_redacted": "      },\n      {\n        \"line\": 22,\n        \"text\": \"\\\"next_action\\\": \\\"Next: produce narrow source patch package for the exact NameError only. No restart/paper/live unless separately approved.\\\",\",\n        \"window_redacted\": \"        \\\"\\\\n      },\\\\n      {\\\\n        \\\",\\n        \\\",\\\\n  \\\"\\n      ]\\n    },\\n    \\\"next_action\\\": \\\"Next: produce narrow source patch package for the exact NameError only. No restart/paper/live unless separately approved.\\\",\\n    \\\"patch_surface\\\": {\\n      \\\"hit_files\\\": [],\\n      \\\"likely_file\\\": null,\\n      \\\"likely_pattern\\\": \\\"UNKNOWN\\\",\"\n      },\n      {\n        \"line\": 31,\n        \"text\": \"\\\"r5x_likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\","
  },
  {
    "line": 22,
    "window_redacted": "        \"window_redacted\": \"        \\\"\\\\n      },\\\\n      {\\\\n        \\\",\\n        \\\",\\\\n  \\\"\\n      ]\\n    },\\n    \\\"next_action\\\": \\\"Next: produce narrow source patch package for the exact NameError only. No restart/paper/live unless separately approved.\\\",\\n    \\\"patch_surface\\\": {\\n      \\\"hit_files\\\": [],\\n      \\\"likely_file\\\": null,\\n      \\\"likely_pattern\\\": \\\"UNKNOWN\\\",\"\n      },\n      {\n        \"line\": 31,\n        \"text\": \"\\\"r5x_likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\",\n        \"window_redacted\": \"      \\\"patch_scope_recommendation\\\": \\\"Prepare a narrow, single-file patch only after reviewing the snippet. Do not alter thresholds, broker/order routing, risk/execution, or paper/live gates.\\\",\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\"\\n    },\\n    \\\"r5x_final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n    \\\"r5x_likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\\n    \\\"r5x_path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n    \\\"standard_services\\\": []\\n  },\\n  \\\"compile_checks\\\": {\"\n      },\n      {\n        \"line\": 37,"
  },
  {
    "line": 23,
    "window_redacted": "      },\n      {\n        \"line\": 31,\n        \"text\": \"\\\"r5x_likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\",\n        \"window_redacted\": \"      \\\"patch_scope_recommendation\\\": \\\"Prepare a narrow, single-file patch only after reviewing the snippet. Do not alter thresholds, broker/order routing, risk/execution, or paper/live gates.\\\",\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\"\\n    },\\n    \\\"r5x_final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n    \\\"r5x_likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\\n    \\\"r5x_path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n    \\\"standard_services\\\": []\\n  },\\n  \\\"compile_checks\\\": {\"\n      },\n      {\n        \"line\": 37,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 27,
    "window_redacted": "        \"window_redacted\": \"      \\\"patch_scope_recommendation\\\": \\\"Prepare a narrow, single-file patch only after reviewing the snippet. Do not alter thresholds, broker/order routing, risk/execution, or paper/live gates.\\\",\\n      \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\"\\n    },\\n    \\\"r5x_final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n    \\\"r5x_likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\\n    \\\"r5x_path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n    \\\"standard_services\\\": []\\n  },\\n  \\\"compile_checks\\\": {\"\n      },\n      {\n        \"line\": 37,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"    \\\"standard_services\\\": []\\n  },\\n  \\\"compile_checks\\\": {\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 41,"
  },
  {
    "line": 28,
    "window_redacted": "      },\n      {\n        \"line\": 37,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"    \\\"standard_services\\\": []\\n  },\\n  \\\"compile_checks\\\": {\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 41,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 32,
    "window_redacted": "        \"window_redacted\": \"    \\\"standard_services\\\": []\\n  },\\n  \\\"compile_checks\\\": {\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 41,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 45,"
  },
  {
    "line": 33,
    "window_redacted": "      },\n      {\n        \"line\": 41,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 45,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 37,
    "window_redacted": "        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 45,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 49,"
  },
  {
    "line": 38,
    "window_redacted": "      },\n      {\n        \"line\": 45,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 49,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 42,
    "window_redacted": "        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 49,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 53,"
  },
  {
    "line": 43,
    "window_redacted": "      },\n      {\n        \"line\": 49,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 53,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 47,
    "window_redacted": "        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/main.py\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 53,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 57,"
  },
  {
    "line": 48,
    "window_redacted": "      },\n      {\n        \"line\": 53,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 57,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 52,
    "window_redacted": "        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 57,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 61,"
  },
  {
    "line": 53,
    "window_redacted": "      },\n      {\n        \"line\": 57,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 61,\n        \"text\": \"\\\"error\\\": null,\","
  },
  {
    "line": 57,
    "window_redacted": "        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\"\n      },\n      {\n        \"line\": 61,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    }\\n  },\\n  \\\"created_at_utc\\\": \\\"2026-05-15T04:57:31.872517+00:00\\\",\"\n      },\n      {\n        \"line\": 67,"
  },
  {
    "line": 58,
    "window_redacted": "      },\n      {\n        \"line\": 61,\n        \"text\": \"\\\"error\\\": null,\",\n        \"window_redacted\": \"      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    },\\n    \\\"/<REDACTED_SECRET_OR_TOKEN>\\\": {\\n      \\\"error\\\": null,\\n      \\\"ok\\\": true\\n    }\\n  },\\n  \\\"created_at_utc\\\": \\\"2026-05-15T04:57:31.872517+00:00\\\",\"\n      },\n      {\n        \"line\": 67,\n        \"text\": \"\\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\","
  },
  {
    "line": 63,
    "window_redacted": "      },\n      {\n        \"line\": 67,\n        \"text\": \"\\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\",\n        \"window_redacted\": \"    }\\n  },\\n  \\\"created_at_utc\\\": \\\"2026-05-15T04:57:31.872517+00:00\\\",\\n  \\\"failures\\\": [],\\n  \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"input_proofs\\\": {\\n    \\\"latest_r5x\\\": {\\n      \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n      \\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\"\n      },\n      {\n        \"line\": 71,\n        \"text\": \"\\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\","
  },
  {
    "line": 67,
    "window_redacted": "        \"window_redacted\": \"    }\\n  },\\n  \\\"created_at_utc\\\": \\\"2026-05-15T04:57:31.872517+00:00\\\",\\n  \\\"failures\\\": [],\\n  \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"input_proofs\\\": {\\n    \\\"latest_r5x\\\": {\\n      \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n      \\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\"\n      },\n      {\n        \"line\": 71,\n        \"text\": \"\\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\",\n        \"window_redacted\": \"  \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"input_proofs\\\": {\\n    \\\"latest_r5x\\\": {\\n      \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n      \\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\\n      \\\"path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\"\\n    }\\n  },\\n  \\\"lane\\\": \\\"A6\\\",\"\n      },\n      {\n        \"line\": 76,"
  },
  {
    "line": 68,
    "window_redacted": "      },\n      {\n        \"line\": 71,\n        \"text\": \"\\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\",\n        \"window_redacted\": \"  \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"input_proofs\\\": {\\n    \\\"latest_r5x\\\": {\\n      \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n      \\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\\n      \\\"path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\"\\n    }\\n  },\\n  \\\"lane\\\": \\\"A6\\\",\"\n      },\n      {\n        \"line\": 76,\n        \"text\": \"\\\"nameerror_extraction\\\": {\","
  },
  {
    "line": 72,
    "window_redacted": "        \"window_redacted\": \"  \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"input_proofs\\\": {\\n    \\\"latest_r5x\\\": {\\n      \\\"final_verdict\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n      \\\"likely_condition\\\": \\\"STRATEGY_EXIT_LOG_CLASSIFIED_NAME_ERROR\\\",\\n      \\\"path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\"\\n    }\\n  },\\n  \\\"lane\\\": \\\"A6\\\",\"\n      },\n      {\n        \"line\": 76,\n        \"text\": \"\\\"nameerror_extraction\\\": {\",\n        \"window_redacted\": \"      \\\"path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\"\\n    }\\n  },\\n  \\\"lane\\\": \\\"A6\\\",\\n  \\\"nameerror_extraction\\\": {\\n    \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n    \\\"symbol_counts\\\": {\\n      \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\\n      \\\"\\\\n      }\\\\n    ],\\\\n    \\\": 1,\"\n      },\n      {\n        \"line\": 91,"
  },
  {
    "line": 73,
    "window_redacted": "      },\n      {\n        \"line\": 76,\n        \"text\": \"\\\"nameerror_extraction\\\": {\",\n        \"window_redacted\": \"      \\\"path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\"\\n    }\\n  },\\n  \\\"lane\\\": \\\"A6\\\",\\n  \\\"nameerror_extraction\\\": {\\n    \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n    \\\"symbol_counts\\\": {\\n      \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\\n      \\\"\\\\n      }\\\\n    ],\\\\n    \\\": 1,\"\n      },\n      {\n        \"line\": 91,\n        \"text\": \"\\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\","
  },
  {
    "line": 77,
    "window_redacted": "        \"window_redacted\": \"      \\\"path\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\"\\n    }\\n  },\\n  \\\"lane\\\": \\\"A6\\\",\\n  \\\"nameerror_extraction\\\": {\\n    \\\"primary_symbol\\\": \\\"\\\\n        },\\\\n        {\\\\n          \\\",\\n    \\\"symbol_counts\\\": {\\n      \\\"\\\\n        },\\\\n        {\\\\n          \\\": 10,\\n      \\\"\\\\n      }\\\\n    ],\\\\n    \\\": 1,\"\n      },\n      {\n        \"line\": 91,\n        \"text\": \"\\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\",\n        \"window_redacted\": \"      \\\"\\\\n      },\\\\n      {\\\\n        \\\",\\n      \\\",\\\\n  \\\"\\n    ]\\n  },\\n  \\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\\n  \\\"orders_mme_stream_xlen\\\": 0,\\n  \\\"paper_live_status\\\": \\\"A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE\\\",\\n  \\\"patch_plan\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"patch_surface\\\": {\"\n      },\n      {\n        \"line\": 93,"
  },
  {
    "line": 78,
    "window_redacted": "      },\n      {\n        \"line\": 91,\n        \"text\": \"\\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\",\n        \"window_redacted\": \"      \\\"\\\\n      },\\\\n      {\\\\n        \\\",\\n      \\\",\\\\n  \\\"\\n    ]\\n  },\\n  \\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\\n  \\\"orders_mme_stream_xlen\\\": 0,\\n  \\\"paper_live_status\\\": \\\"A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE\\\",\\n  \\\"patch_plan\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"patch_surface\\\": {\"\n      },\n      {\n        \"line\": 93,\n        \"text\": \"\\\"paper_live_status\\\": \\\"A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE\\\",\","
  },
  {
    "line": 83,
    "window_redacted": "      },\n      {\n        \"line\": 93,\n        \"text\": \"\\\"paper_live_status\\\": \\\"A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE\\\",\",\n        \"window_redacted\": \"    ]\\n  },\\n  \\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\\n  \\\"orders_mme_stream_xlen\\\": 0,\\n  \\\"paper_live_status\\\": \\\"A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE\\\",\\n  \\\"patch_plan\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"patch_surface\\\": {\\n    \\\"hit_files\\\": [],\\n    \\\"likely_file\\\": null,\"\n      },\n      {\n        \"line\": 94,\n        \"text\": \"\\\"patch_plan\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\","
  },
  {
    "line": 88,
    "window_redacted": "      },\n      {\n        \"line\": 94,\n        \"text\": \"\\\"patch_plan\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\",\n        \"window_redacted\": \"  },\\n  \\\"next_rule\\\": \\\"If PASS, next may be a narrow source patch for exact NameError only, with no paper/live/risk/execution/order changes.\\\",\\n  \\\"orders_mme_stream_xlen\\\": 0,\\n  \\\"paper_live_status\\\": \\\"A6-PAPER_BLOCKED_NO_PAPER_NO_LIVE\\\",\\n  \\\"patch_plan\\\": \\\"/<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"patch_surface\\\": {\\n    \\\"hit_files\\\": [],\\n    \\\"likely_file\\\": null,\\n    \\\"likely_pattern\\\": \\\"UNKNOWN\\\",\"\n      },\n      {\n        \"line\": 105,\n        \"text\": \"\\\"decision_id\\\": \\\"broker_order_id\\\",\","
  },
  {
    "line": 98,
    "window_redacted": "      },\n      {\n        \"line\": 118,\n        \"text\": \"\\\"purpose\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\",\n        \"window_redacted\": \"    \\\"flat\\\": true,\\n    \\\"type\\\": \\\"hash\\\"\\n  },\\n  \\\"processes\\\": [],\\n  \\\"purpose\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"required_true\\\": {\\n    \\\"all_watched_sources_compile\\\": true,\\n    \\\"exact_nameerror_symbol_extracted\\\": true,\\n    \\\"latest_r5x_proof_found\\\": true,\"\n      },\n      {\n        \"line\": 121,\n        \"text\": \"\\\"exact_nameerror_symbol_extracted\\\": true,\","
  },
  {
    "line": 102,
    "window_redacted": "        \"window_redacted\": \"    \\\"flat\\\": true,\\n    \\\"type\\\": \\\"hash\\\"\\n  },\\n  \\\"processes\\\": [],\\n  \\\"purpose\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"required_true\\\": {\\n    \\\"all_watched_sources_compile\\\": true,\\n    \\\"exact_nameerror_symbol_extracted\\\": true,\\n    \\\"latest_r5x_proof_found\\\": true,\"\n      },\n      {\n        \"line\": 121,\n        \"text\": \"\\\"exact_nameerror_symbol_extracted\\\": true,\",\n        \"window_redacted\": \"  \\\"processes\\\": [],\\n  \\\"purpose\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"required_true\\\": {\\n    \\\"all_watched_sources_compile\\\": true,\\n    \\\"exact_nameerror_symbol_extracted\\\": true,\\n    \\\"latest_r5x_proof_found\\\": true,\\n    \\\"no_broker_order\\\": true,\\n    \\\"no_lock_clear_delete\\\": true,\\n    \\\"no_paper_live\\\": true,\"\n      },\n      {\n        \"line\": 124,"
  },
  {
    "line": 103,
    "window_redacted": "      },\n      {\n        \"line\": 121,\n        \"text\": \"\\\"exact_nameerror_symbol_extracted\\\": true,\",\n        \"window_redacted\": \"  \\\"processes\\\": [],\\n  \\\"purpose\\\": \\\"<REDACTED_SECRET_OR_TOKEN>\\\",\\n  \\\"required_true\\\": {\\n    \\\"all_watched_sources_compile\\\": true,\\n    \\\"exact_nameerror_symbol_extracted\\\": true,\\n    \\\"latest_r5x_proof_found\\\": true,\\n    \\\"no_broker_order\\\": true,\\n    \\\"no_lock_clear_delete\\\": true,\\n    \\\"no_paper_live\\\": true,\"\n      },\n      {\n        \"line\": 124,\n        \"text\": \"\\\"no_lock_clear_delete\\\": true,\","
  },
  {
    "line": 108,
    "window_redacted": "      },\n      {\n        \"line\": 124,\n        \"text\": \"\\\"no_lock_clear_delete\\\": true,\",\n        \"window_redacted\": \"    \\\"all_watched_sources_compile\\\": true,\\n    \\\"exact_nameerror_symbol_extracted\\\": true,\\n    \\\"latest_r5x_proof_found\\\": true,\\n    \\\"no_broker_order\\\": true,\\n    \\\"no_lock_clear_delete\\\": true,\\n    \\\"no_paper_live\\\": true,\\n    \\\"no_patch\\\": true,\\n    \\\"no_redis_write\\\": true,\\n    \\\"no_restore\\\": true,\"\n      },\n      {\n        \"line\": 133,\n        \"text\": \"\\\"r5x_nameerror_classification_found\\\": true,\","
  },
  {
    "line": 112,
    "window_redacted": "        \"window_redacted\": \"    \\\"all_watched_sources_compile\\\": true,\\n    \\\"exact_nameerror_symbol_extracted\\\": true,\\n    \\\"latest_r5x_proof_found\\\": true,\\n    \\\"no_broker_order\\\": true,\\n    \\\"no_lock_clear_delete\\\": true,\\n    \\\"no_paper_live\\\": true,\\n    \\\"no_patch\\\": true,\\n    \\\"no_redis_write\\\": true,\\n    \\\"no_restore\\\": true,\"\n      },\n      {\n        \"line\": 133,\n        \"text\": \"\\\"r5x_nameerror_classification_found\\\": true,\",\n        \"window_redacted\": \"    \\\"no_risk_execution_order_process_visible\\\": true,\\n    \\\"no_service_start_restart_stop\\\": true,\\n    \\\"orders_mme_stream_zero_or_absent\\\": true,\\n    \\\"position_flat\\\": true,\\n    \\\"r5x_nameerror_classification_found\\\": true,\\n    \\\"traceback_or_source_context_extracted\\\": true,\\n    \\\"watched_sources_unchanged_by_this_batch\\\": true\\n  },\\n  \\\"safety\\\": {\"\n      },\n      {\n        \"line\": 134,"
  },
  {
    "line": 113,
    "window_redacted": "      },\n      {\n        \"line\": 133,\n        \"text\": \"\\\"r5x_nameerror_classification_found\\\": true,\",\n        \"window_redacted\": \"    \\\"no_risk_execution_order_process_visible\\\": true,\\n    \\\"no_service_start_restart_stop\\\": true,\\n    \\\"orders_mme_stream_zero_or_absent\\\": true,\\n    \\\"position_flat\\\": true,\\n    \\\"r5x_nameerror_classification_found\\\": true,\\n    \\\"traceback_or_source_context_extracted\\\": true,\\n    \\\"watched_sources_unchanged_by_this_batch\\\": true\\n  },\\n  \\\"safety\\\": {\"\n      },\n      {\n        \"line\": 134,\n        \"text\": \"\\\"traceback_or_source_context_extracted\\\": true,\","
  },
  {
    "line": 117,
    "window_redacted": "        \"window_redacted\": \"    \\\"no_risk_execution_order_process_visible\\\": true,\\n    \\\"no_service_start_restart_stop\\\": true,\\n    \\\"orders_mme_stream_zero_or_absent\\\": true,\\n    \\\"position_flat\\\": true,\\n    \\\"r5x_nameerror_classification_found\\\": true,\\n    \\\"traceback_or_source_context_extracted\\\": true,\\n    \\\"watched_sources_unchanged_by_this_batch\\\": true\\n  },\\n  \\\"safety\\\": {\"\n      },\n      {\n        \"line\": 134,\n        \"text\": \"\\\"traceback_or_source_context_extracted\\\": true,\",\n        \"window_redacted\": \"    \\\"no_service_start_restart_stop\\\": true,\\n    \\\"orders_mme_stream_zero_or_absent\\\": true,\\n    \\\"position_flat\\\": true,\\n    \\\"r5x_nameerror_classification_found\\\": true,\\n    \\\"traceback_or_source_context_extracted\\\": true,\\n    \\\"watched_sources_unchanged_by_this_batch\\\": true\\n  },\\n  \\\"safety\\\": {\\n    \\\"broker_order_executed\\\": false,\"\n      },\n      {\n        \"line\": 139,"
  }
]
```

Next rule:
- If command-shape/argparse mismatch: inspect exact main.py service CLI contract before patch.
- If lock/consumer-group gate: inspect Redis key/group state before any mutation.
- If source exception: produce narrow patch plan only for exact source error.
- No paper/live/risk/execution/order work from this batch.
