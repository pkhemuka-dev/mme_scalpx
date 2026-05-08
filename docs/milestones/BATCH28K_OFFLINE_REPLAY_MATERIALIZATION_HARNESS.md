Batch 28K Offline replay materialization harness

Date: 2026-05-01

Verdict:
PASS_OBSERVE_ONLY_OFFLINE_REPLAY_MATERIALIZATION_HARNESS_28K

Accepted for:
OFFLINE_REPLAY_MATERIALIZATION_HARNESS_ONLY

Source:
- 28J preflight: etc/replay/parity/observe_only_replay_input_dataset_preflight_28j.json
- closed 28F package root: run/replay/parity/live_evidence/pstrategy_20260430_094557
- final evidence map: etc/replay/parity/observe_only_actual_generated_evidence_map.json

Generated:
- bin/observe_only_offline_replay_materialization_harness_28k.py
- etc/replay/parity/observe_only_offline_replay_materialization_harness_28k.json
- run/proofs/proof_observe_only_offline_replay_materialization_harness_28k.json
- run/proofs/proof_observe_only_offline_replay_materialization_harness_28k_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/00_offline_materialization_harness_manifest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/01_dataset_source_reference_index.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/02_service_surface_materialization_plan.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/03_no_enablement_boundary.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/04_future_execution_contract.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/05_materialization_readiness.json

Purpose:
28K builds only the offline replay materialization harness from the 28J preflight.
It does not run replay.
It does not materialize a replay dataset yet.
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
full_live_replay_parity=NOT_PROVEN_IN_28K

Next:
Batch 28L — run offline replay materialization dry-run from the 28K harness, still not paper/live enablement.
