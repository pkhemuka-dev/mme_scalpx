# 26-O22-R6 — controlled-paper approved-start command template generator

- generated_at_utc: 2026-05-06T09:49:47.934241+00:00
- tag: `batch26o22_r6_controlled_paper_approved_start_template_generator_20260506_151947`
- proof: `run/proofs/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json`
- manifest: `run/proofs/manifest_batch26o22_r6_controlled_paper_approved_start_template_generator.json`
- start_template: `run/live_capture/batch26o22_r6_controlled_paper_approved_start_template_generator_20260506_151947/CONTROLLED_PAPER_START_TEMPLATE_NOT_APPROVED_o22_r6.sh`
- stop_template: `run/live_capture/batch26o22_r6_controlled_paper_approved_start_template_generator_20260506_151947/CONTROLLED_PAPER_STOP_TEMPLATE_o22_r6.sh`
- template_json: `run/live_capture/batch26o22_r6_controlled_paper_approved_start_template_generator_20260506_151947/controlled_paper_approved_start_template_o22_r6.json`
- gate_json: `run/live_capture/batch26o22_r6_controlled_paper_approved_start_template_generator_20260506_151947/controlled_paper_start_gate_o22_r6.json`
- backup_dir: `run/_code_backups/batch26o22_r6_controlled_paper_approved_start_template_generator_20260506_151947`

## Purpose
- Generate a locked future controlled-paper start template.
- This batch does not approve or start controlled paper.
- Template files are intentionally non-executable by default.

## Future explicit approval phrase
`APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE`

## Scope locked
- MIST CALL only.
- 1 lot only.
- paper/sandbox route only.
- real_live=false.
- no automatic broker failover.
- no mid-position provider migration.
- FLAT position before entry.

## Safety
- No service start.
- No broker call.
- No order write.
- No real live.
- No source patch.

## Verdict
- final_verdict: `PASS_O22_R6_CONTROLLED_PAPER_TEMPLATE_GENERATOR_OK_LOCKED_NO_START`
- false_keys: `[]`
- next_recommended_batch: `26-O22-R7 exact CLI flag validator for controlled-paper start template; still no actual start unless explicitly approved.`

## Required verdicts
```json
{
  "approval_gate_locked_template_only": true,
  "compile_pass": true,
  "execution_not_running": true,
  "gate_json_written": true,
  "import_pass": true,
  "no_broker_call": true,
  "no_controlled_paper_runtime_env": true,
  "no_forced_candidate": true,
  "no_order_write_intent": true,
  "no_paper_start": true,
  "no_scope_ack_env": true,
  "no_threshold_relaxation": true,
  "o22_r5_false_keys_empty": true,
  "o22_r5_gate_locked": true,
  "o22_r5_paper_start_allowed_false": true,
  "o22_r5_pass_loaded": true,
  "orders_zero": true,
  "paper_start_allowed_by_this_batch_false": true,
  "position_flat": true,
  "production_source_patch_false": true,
  "real_live_false": true,
  "risk_not_running": true,
  "service_start_false": true,
  "stop_template_not_executable_by_default": true,
  "stop_template_sh_written": true,
  "template_json_written": true,
  "template_not_executable_by_default": true,
  "template_sh_written": true
}
```