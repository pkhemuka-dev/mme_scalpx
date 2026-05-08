# AI Patch Runner v0.2.2 — Safety Policy + Blocked-Path Registry

UTC: 20260508T164441Z

## Result

PASS.

## Created / Updated

- `ai_patch_runner/policy/ai_patch_policy.json`
- `ai_patch_runner/policy/ai_patch_policy.md`
- `ai_patch_runner/policy/check_policy.py`

## Purpose

This batch freezes the AI Patch Runner safety boundary before v0.3 sandbox patching.

## Current permitted runner capabilities

- Generate command packages
- Save generated scripts
- Static-validate generated scripts
- Classify manual-run output
- Run health checks

## Current forbidden runner capabilities

- Execute generated scripts automatically
- Patch real project trading-control files
- Start services
- Call brokers
- Place orders
- Write live Redis trading truth
- Enable paper/live

## Protected surfaces

Automatic patching is blocked or requires human review for:

- `app/`
- `etc/`
- `bin/`
- `scripts/`
- `systemd/`
- `deployment/`
- `common/secrets/`
- broker/execution/risk/main/provider runtime surfaces

## Self-test

Policy checker self-test passed.

## Safety

- broker_calls_executed=false
- service_starts_executed=false
- live_redis_writes_executed=false
- paper_or_live_enabled=false
- generated_scripts_executed_by_runner=false
- real_project_trading_code_patched=false

## Artifacts

- Proof: `run/proofs/proof_ai_patch_runner_v022_safety_policy_20260508T164441Z.json`
- Self-test: `run/proofs/ai_patch_runner_v022_safety_policy_20260508T164441Z_self_test.json`
- Audit: `run/audits/ai_patch_runner_v022_safety_policy_20260508T164441Z.txt`
- Backups: `run/_code_backups/ai_patch_runner_v022_safety_policy_20260508T164441Z`
