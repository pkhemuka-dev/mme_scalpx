# 26-O22-R7-R2 — exact CLI flag validator template-writer repair

- generated_at_utc: 2026-05-06T09:53:03.981628+00:00
- tag: `batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair_20260506_152302`
- proof: `run/proofs/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json`
- manifest: `run/proofs/manifest_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json`
- cli_validation: `run/live_capture/batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair_20260506_152302/controlled_paper_cli_flag_validation_o22_r7_r2.json`
- validated_template: `run/live_capture/batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair_20260506_152302/CONTROLLED_PAPER_START_TEMPLATE_VALIDATED_NOT_APPROVED_o22_r7_r2.sh`
- start_plan: `run/live_capture/batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair_20260506_152302/controlled_paper_start_plan_validated_o22_r7_r2.json`
- backup_dir: `run/_code_backups/batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair_20260506_152302`

## Purpose
- Repair R7 template-writer bug only.
- Validate current `app.mme_scalpx.main` CLI surfaces.
- Generate a validated but still locked start template.
- Keep all service start lines commented out.
- No paper start, no service start, no broker call, no order write, no source patch.

## Future explicit approval phrase
`APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE`

## Verdict
- final_verdict: `PASS_O22_R7_R2_EXACT_CLI_FLAG_VALIDATOR_OK_LOCKED_NO_START`
- false_keys: `[]`
- next_recommended_batch: `26-O22-R8 final controlled-paper go/no-go evidence pack; still no actual start unless explicit user approval.`

## Required verdicts
```json
{
  "compile_pass": true,
  "execution_not_running": true,
  "import_pass": true,
  "main_cli_service_flag_present": true,
  "main_help_invocation_safe": true,
  "no_broker_call": true,
  "no_controlled_paper_runtime_env": true,
  "no_forced_candidate": true,
  "no_order_write_intent": true,
  "no_paper_start": true,
  "no_scope_ack_env": true,
  "no_threshold_relaxation": true,
  "o22_r6_false_keys_empty": true,
  "o22_r6_paper_start_allowed_false": true,
  "o22_r6_pass_loaded": true,
  "o22_r6_template_written": true,
  "o22_r7_failure_loaded": true,
  "o22_r7_failure_was_template_writer_typeerror": true,
  "orders_zero": true,
  "paper_start_allowed_by_this_batch_false": true,
  "position_flat": true,
  "production_source_patch_false": true,
  "real_live_false": true,
  "risk_not_running": true,
  "service_command_count_is_5": true,
  "service_commands_commented_out": true,
  "service_start_false": true,
  "start_plan_json_written": true,
  "validated_template_not_executable_by_default": true,
  "validated_template_written": true
}
```