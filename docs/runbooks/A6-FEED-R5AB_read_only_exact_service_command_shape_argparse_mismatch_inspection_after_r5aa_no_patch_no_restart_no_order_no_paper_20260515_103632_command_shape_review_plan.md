# A6-FEED-R5AB_read_only_exact_service_command_shape_argparse_mismatch_inspection_after_r5aa_no_patch_no_restart_no_order_no_paper_20260515_103632 Command-Shape Review Plan

Batch: A6-FEED-R5AB

Verdict: PASS_A6_FEED_R5AB_R5AA_ARGPARSE_SIGNAL_NEEDS_LOG_LINE_REVIEW_MINIMAL_COMMAND_OK_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only inspection only; no patch, no start/restart/stop, no Redis write, no paper/live, no broker/order, no risk/execution.

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

Parser contract:

```json
{
  "accepted_option_strings": [
    "--bootstrap-provider",
    "--doctor",
    "--replay-start-wall-time-ns",
    "--service",
    "--skip-group-bootstrap"
  ],
  "raw_contains": {
    "--bootstrap-provider": true,
    "--service": true,
    "--skip-group-bootstrap": true,
    "bootstrap_provider": true,
    "skip_group_bootstrap": true
  },
  "service_choices": []
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

Next rule:
- If unsupported CLI args are confirmed, patch only command construction or CLI contract after explicit plan.
- Do not change strategy thresholds, family logic, risk, execution, paper/live, broker routing, or order behavior.
- No service retry until explicit observe-only approval.
