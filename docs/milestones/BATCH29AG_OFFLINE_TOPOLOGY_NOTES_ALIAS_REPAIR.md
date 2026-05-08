BATCH 29AG OFFLINE TOPOLOGY NOTES ALIAS REPAIR

generated_at_utc: 2026-05-02T06:43:17.011158+00:00
verdict: FAIL_29AG_TOPOLOGY_NOTES_ALIAS_STATIC_PROOF_FAILED
patch_applied: True
topology_notes_alias_present: True
topology_notes_probe_ok: False
topology_notes_gap_resolved: False
retry_returncode: None
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'notes'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29AG
repair_path: STATIC_PROOF_REPAIR_REQUIRED
next_batch: Repair topology notes static/probe failure before guarded ReplayEngine retry.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- app/mme_scalpx/replay/offline_context_shim.py

Proofs:
- run/proofs/proof_offline_topology_notes_alias_repair_29ag.json
- run/proofs/proof_offline_topology_notes_alias_repair_29ag_latest.json
- run/proofs/batch29ag_offline_topology_notes_alias_repair_20260502_121316_driver_proof.json
- etc/replay/parity/offline_topology_notes_alias_repair_29ag.json
