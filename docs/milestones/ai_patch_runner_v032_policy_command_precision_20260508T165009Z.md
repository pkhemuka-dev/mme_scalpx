# AI Patch Runner v0.3.2 — Policy Command Precision Repair

UTC: 20260508T165009Z

## Result

PASS.

## Why this was needed

v0.3.1 failed safely because the policy checker treated the harmless prose word `services` inside the sandbox diff as if it were an executable `service` command.

## What changed

`ai_patch_runner/policy/check_policy.py` now performs line-aware command detection:

- harmless prose like “external services” is allowed
- harmless unified diff text is allowed
- actual commands like `sudo service redis-server restart` remain blocked
- `nohup`, `systemctl`, Redis mutations, and app main service starts remain blocked

## Rerun result

The AI-generated sandbox patch rerun passed.

## Safety

- broker_calls_executed=false
- service_starts_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- generated_scripts_executed_by_runner=false
- real_project_trading_code_patched=false
- sandbox_only_patch_applied=true

## Artifacts

- Proof: `run/proofs/proof_ai_patch_runner_v032_policy_command_precision_20260508T165009Z.json`
- Sandbox report: `ai_patch_runner/sandbox/ai_patch_runner_v032_policy_command_precision_20260508T165009Z/sandbox_report.json`
- Sandbox diff: `ai_patch_runner/sandbox/ai_patch_runner_v032_policy_command_precision_20260508T165009Z/sandbox.diff`
- AI patch plan: `ai_patch_runner/sandbox/ai_patch_runner_v032_policy_command_precision_20260508T165009Z/ai_patch_plan.json`
- AI classification: `ai_patch_runner/sandbox/ai_patch_runner_v032_policy_command_precision_20260508T165009Z/ai_classification.json`
- Audit: `run/audits/ai_patch_runner_v032_policy_command_precision_20260508T165009Z.txt`
- Backups: `run/_code_backups/ai_patch_runner_v032_policy_command_precision_20260508T165009Z`
