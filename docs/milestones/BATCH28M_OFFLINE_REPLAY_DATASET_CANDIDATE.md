Batch 28M Offline replay dataset candidate materialization

Date: 2026-05-01

Verdict:
PASS_OBSERVE_ONLY_OFFLINE_REPLAY_DATASET_CANDIDATE_28M

Accepted for:
OFFLINE_REPLAY_DATASET_CANDIDATE_ONLY

Source:
- 28L dry-run proof: run/proofs/proof_observe_only_offline_replay_materialization_dry_run_28l_latest.json
- 28L dry-run root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate
- closed observe_only evidence package converted through 28K/28L harness chain

Generated:
- bin/observe_only_offline_replay_dataset_candidate_materialize_28m.py
- etc/replay/parity/observe_only_offline_replay_dataset_candidate_28m.json
- run/proofs/proof_observe_only_offline_replay_dataset_candidate_28m.json
- run/proofs/proof_observe_only_offline_replay_dataset_candidate_28m_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/00_dataset_candidate_manifest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/01_source_evidence_catalog.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/02_materialized_file_index.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/03_service_surface_dataset_plan.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/04_no_broker_no_live_redis_boundary.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/05_candidate_readiness.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/06_next_replay_dry_run_contract.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate/input_surfaces/

Purpose:
28M materializes only an offline replay dataset candidate from the 28L dry-run.
It copies and indexes input surfaces under run/replay.
It does not run the replay engine.
It does not produce replay outputs.
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
full_live_replay_parity=NOT_PROVEN_IN_28M

Next:
Batch 28N — build no-broker/no-live-Redis proof for offline replay dataset candidate before any replay engine dry-run.
