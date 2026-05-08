# AI Patch Runner Policy v0.2.2

## Purpose

This policy freezes the safety boundary for the MME-ScalpX AI Patch Runner before sandbox patching is introduced.

The AI runner may currently:

- generate command packages
- save generated scripts
- statically validate generated scripts
- classify manual-run logs
- run its own health checks

The AI runner may **not** currently:

- execute generated scripts automatically
- patch real project trading-control files
- start services
- call brokers
- place orders
- write live Redis trading truth
- enable paper trading
- enable real live trading

## Allowed auto-touch areas

- `ai_patch_runner/`
- `run/proofs/`
- `run/audits/`
- `run/_code_backups/`
- `docs/milestones/`
- `docs/runbooks/`

## Human-review required areas

- `app/`
- `etc/`
- `bin/`
- `scripts/`
- `systemd/`
- `deployment/`
- `common/secrets/`

## Blocked from automatic patching

- `app/mme_scalpx/main.py`
- `app/mme_scalpx/services/execution.py`
- `app/mme_scalpx/services/risk.py`
- broker/login/execution/provider runtime integration files
- `etc/brokers/`
- `.env` files
- secret/credential files
- systemd/deployment files

## Blocked runtime actions

- `nohup`
- `systemctl`
- starting `app.mme_scalpx.main`
- Redis writes such as `SET`, `HSET`, `XADD`, `DEL`
- any paper/live enablement environment flags

## Future v0.3 boundary

v0.3 may create a sandbox workspace and patch only that sandbox. It must produce a diff and proof bundle for human review. It must not apply patches to the real project.

## Required safety flags

Every runner batch proof must preserve:

- `broker_calls_executed=false`
- `service_starts_executed=false`
- `live_redis_writes_executed=false`
- `paper_or_live_enabled=false`
- `generated_scripts_executed_by_runner=false`
