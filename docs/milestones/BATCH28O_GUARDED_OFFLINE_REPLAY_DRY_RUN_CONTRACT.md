Batch 28O Guarded offline replay engine dry-run command contract

Date: 2026-05-01

Verdict:
PASS_GUARDED_OFFLINE_REPLAY_DRY_RUN_CONTRACT_28O

Accepted for:
GUARDED_OFFLINE_REPLAY_DRY_RUN_COMMAND_CONTRACT_ONLY

Source:
- 28N no-broker/no-live-Redis proof: run/proofs/proof_observe_only_offline_replay_candidate_no_broker_no_live_redis_28n_latest.json
- 28M dataset candidate proof: run/proofs/proof_observe_only_offline_replay_dataset_candidate_28m_latest.json
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate
- safety gate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/no_broker_no_live_redis_gate

Generated:
- bin/prepare_guarded_offline_replay_dry_run_contract_28o.py
- etc/replay/parity/guarded_offline_replay_dry_run_contract_28o.json
- run/proofs/proof_guarded_offline_replay_dry_run_contract_28o.json
- run/proofs/proof_guarded_offline_replay_dry_run_contract_28o_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_contract/

Purpose:
28O prepares only the guarded offline replay engine dry-run command contract.
It does not execute the proposed command.
It does not run the replay engine.
It does not compare replay/live parity.
It does not approve paper_armed or live trading.

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
full_live_replay_parity=NOT_PROVEN_IN_28O

Next:
Batch 28P — execute guarded offline replay engine dry-run only if 28O contract is still valid, still not paper/live enablement.
