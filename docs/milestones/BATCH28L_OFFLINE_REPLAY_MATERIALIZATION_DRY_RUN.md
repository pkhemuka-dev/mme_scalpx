Batch 28L Offline replay materialization dry-run

Date: 2026-05-01

Verdict:
PASS_OBSERVE_ONLY_OFFLINE_REPLAY_MATERIALIZATION_DRY_RUN_28L

Accepted for:
OFFLINE_REPLAY_MATERIALIZATION_DRY_RUN_ONLY

Source:
- 28K harness manifest: etc/replay/parity/observe_only_offline_replay_materialization_harness_28k.json
- 28K proof: run/proofs/proof_observe_only_offline_replay_materialization_harness_28k_latest.json
- 28J preflight package: etc/replay/parity/observe_only_replay_input_dataset_preflight_28j.json
- closed observe_only package root: run/replay/parity/live_evidence/pstrategy_20260430_094557

Generated:
- bin/observe_only_offline_replay_materialization_dry_run_28l.py
- etc/replay/parity/observe_only_offline_replay_materialization_dry_run_28l.json
- run/proofs/proof_observe_only_offline_replay_materialization_dry_run_28l.json
- run/proofs/proof_observe_only_offline_replay_materialization_dry_run_28l_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/00_dataset_materialization_dry_run_manifest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/01_input_surface_catalog.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/02_replay_dataset_candidate_index.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/03_service_surface_feasibility.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/04_no_broker_no_live_redis_boundary.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/05_materialization_gap_report.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dry_run_candidate/06_next_materialization_contract.json

Purpose:
28L runs only an offline materialization dry-run from the 28K harness.
It catalogs input surfaces and dataset-candidate feasibility.
It does not materialize replay frames.
It does not run replay.
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
full_live_replay_parity=NOT_PROVEN_IN_28L

Next:
Batch 28M — materialize offline replay dataset candidate from the 28L dry-run, still not paper/live enablement.
