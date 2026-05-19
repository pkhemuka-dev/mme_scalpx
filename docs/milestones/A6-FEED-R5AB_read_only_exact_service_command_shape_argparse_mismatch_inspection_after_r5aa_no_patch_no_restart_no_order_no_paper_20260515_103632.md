# A6-FEED-R5AB_read_only_exact_service_command_shape_argparse_mismatch_inspection_after_r5aa_no_patch_no_restart_no_order_no_paper_20260515_103632

Batch: A6-FEED-R5AB

Purpose: read_only_exact_service_command_shape_argparse_mismatch_inspection_after_r5aa_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5AB_R5AA_ARGPARSE_SIGNAL_NEEDS_LOG_LINE_REVIEW_MINIMAL_COMMAND_OK_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only command-shape / argparse mismatch inspection only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "argparse_hit_count_from_r5aa": 30,
  "likely_condition": "ARGPARSE_SIGNAL_PRESENT_BUT_CURRENT_MINIMAL_FEATURES_STRATEGY_COMMANDS_MATCH_MAIN_CLI",
  "minimal_commands_ok_against_parser": true,
  "next_action": "Review R5AA windows; next can produce a safer start command plan using minimal supported args only. No restart until explicit approval.",
  "parser_accepted_options": [
    "--bootstrap-provider",
    "--doctor",
    "--replay-start-wall-time-ns",
    "--service",
    "--skip-group-bootstrap"
  ],
  "parser_service_choices": [],
  "r5aa_final_verdict": "PASS_A6_FEED_R5AA_ACTUAL_HIGH_SIGNAL_EXIT_GATE_SIGNATURE_CLASSIFIED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5aa_likely_condition": "SERVICE_COMMAND_SHAPE_OR_ARGPARSE_MISMATCH",
  "r5aa_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AA_read_only_classify_actual_high_signal_exit_gate_signature_from_r5z_no_patch_no_restart_no_order_no_paper_20260515_103437.json",
  "r5u_command_count": 0,
  "r5u_final_verdict": "BLOCKED_A6_FEED_R5U_STARTED_OR_ATTEMPTED_BUT_READINESS_INCOMPLETE_NO_ORDER_NO_PAPER",
  "r5u_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5U_approved_observe_only_features_strategy_start_after_pstackcheck_no_paper_no_order_no_risk_execution_20260515_101356.json",
  "standard_services": [],
  "unknown_or_invalid_commands": []
}
```

Command comparisons:

```json
[
  {
    "command": [
      ".venv/bin/python",
      "-m",
      "app.mme_scalpx.main",
      "--service",
      "features"
    ],
    "command_shape_ok_against_static_parser": true,
    "option_tokens": [
      "--service"
    ],
    "service_choice_valid": true,
    "service_choices": [],
    "service_value": "features",
    "source_path": "current_minimal.features",
    "unknown_options": []
  },
  {
    "command": [
      ".venv/bin/python",
      "-m",
      "app.mme_scalpx.main",
      "--service",
      "strategy"
    ],
    "command_shape_ok_against_static_parser": true,
    "option_tokens": [
      "--service"
    ],
    "service_choice_valid": true,
    "service_choices": [],
    "service_value": "strategy",
    "source_path": "current_minimal.strategy",
    "unknown_options": []
  }
]
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5aa_proof_found": true,
  "latest_r5u_proof_found": true,
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
  "r5aa_command_shape_condition_found": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AB_read_only_exact_service_command_shape_argparse_mismatch_inspection_after_r5aa_no_patch_no_restart_no_order_no_paper_20260515_103632.json
- Plan: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AB_read_only_exact_service_command_shape_argparse_mismatch_inspection_after_r5aa_no_patch_no_restart_no_order_no_paper_20260515_103632_command_shape_review_plan.md
