Batch 28N No-broker/no-live-Redis gate before offline replay dry-run

Date: 2026-05-01

Verdict:
PASS_OBSERVE_ONLY_OFFLINE_REPLAY_CANDIDATE_NO_BROKER_NO_LIVE_REDIS_28N

Accepted for:
NO_BROKER_NO_LIVE_REDIS_GATE_BEFORE_REPLAY_DRY_RUN

Source:
- 28M dataset candidate proof: run/proofs/proof_observe_only_offline_replay_dataset_candidate_28m_latest.json
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate
- replay entrypoint files inspected as inventory only

Generated:
- bin/proof_observe_only_offline_replay_candidate_no_broker_no_live_redis_28n.py
- etc/replay/parity/observe_only_offline_replay_candidate_no_broker_no_live_redis_28n.json
- run/proofs/proof_observe_only_offline_replay_candidate_no_broker_no_live_redis_28n.json
- run/proofs/proof_observe_only_offline_replay_candidate_no_broker_no_live_redis_28n_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/no_broker_no_live_redis_gate/

Purpose:
28N proves the offline replay dataset candidate has a no-broker/no-live-Redis safety gate before any replay engine dry-run.
It inspects replay entrypoint files as inventory only.
It does not run the replay engine.
It does not materialize replay-run frames.
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
full_live_replay_parity=NOT_PROVEN_IN_28N

Next:
Batch 28O — prepare guarded offline replay engine dry-run command contract, still not paper/live enablement.
