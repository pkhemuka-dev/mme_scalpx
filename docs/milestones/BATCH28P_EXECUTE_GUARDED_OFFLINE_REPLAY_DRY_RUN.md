Batch 28P Execute guarded offline replay engine dry-run

Date: 2026-05-01

Verdict:
FAIL_GUARDED_OFFLINE_REPLAY_DRY_RUN_EXECUTION_28P

Accepted for:
GUARDED_OFFLINE_REPLAY_DRY_RUN_EXECUTION_ONLY

Source:
- 28O guarded command contract: run/proofs/proof_guarded_offline_replay_dry_run_contract_28o_latest.json
- contract root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_contract
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate

Generated:
- bin/execute_guarded_offline_replay_dry_run_28p.py
- etc/replay/parity/guarded_offline_replay_dry_run_execution_28p.json
- run/proofs/proof_guarded_offline_replay_dry_run_execution_28p.json
- run/proofs/proof_guarded_offline_replay_dry_run_execution_28p_latest.json
- run/replay/parity/offline_replay_dry_run/observe_only_replay_input_9c50b37fb4782fb0/

Purpose:
28P executes only the guarded offline replay dry-run command from the 28O contract if that contract is still valid.
It does not approve paper_armed.
It does not approve live trading.
It does not compare replay/live parity.
It does not claim full parity.

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
full_live_replay_parity=NOT_PROVEN_IN_28P

Next:
Repair guarded offline replay dry-run command/interface before comparison.
