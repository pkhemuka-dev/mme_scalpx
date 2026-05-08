Batch 28P-R2 Guarded replay CLI adapter / compatibility repair

Date: 2026-05-01

Verdict:
PASS_GUARDED_OFFLINE_REPLAY_DRY_RUN_ADAPTER_28P_R2

Accepted for:
GUARDED_REPLAY_CLI_ADAPTER_COMPATIBILITY_ONLY

Reason:
28P failed with returncode 2 because the current bin/replay_run.py does not support the 28O guarded flags.
28P-R1 confirmed missing guarded flags and required an adapter.
28P-R2 creates an external guarded adapter instead of mutating live strategy/risk/execution/runtime code.

Generated:
- bin/guarded_offline_replay_dry_run_adapter_28p_r2.py
- etc/replay/parity/guarded_offline_replay_dry_run_adapter_28p_r2.json
- run/proofs/proof_guarded_offline_replay_dry_run_adapter_28p_r2.json
- run/proofs/proof_guarded_offline_replay_dry_run_adapter_28p_r2_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_cli_adapter_28p_r2/

Result:
adapter_ready=true
future_command_executed=false
adapter_executed_replay_engine=false
replay_run_completed=false
comparison_completed=false
replay_run_missing_guarded_flags=['--offline', '--dataset-candidate', '--output-root', '--no-broker', '--no-live-redis', '--observe-only', '--dry-run']

Safety:
starts_services=false
reads_live_redis=false
writes_live_redis=false
calls_broker_api=false
paper_armed_approved=false
live_trading_approved=false
execution_arming_created=false
real_order_sent=false
production_doctrine_changed=false
full_live_replay_parity=NOT_PROVEN_IN_28P_R2

Next:
Batch 28P-R3 — execute guarded offline replay dry-run through the 28P-R2 adapter, still not paper/live enablement.
