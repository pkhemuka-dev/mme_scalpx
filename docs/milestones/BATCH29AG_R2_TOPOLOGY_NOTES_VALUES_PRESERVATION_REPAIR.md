BATCH 29AG-R2 TOPOLOGY NOTES VALUES PRESERVATION REPAIR

generated_at_utc: 2026-05-02T06:46:40.028562+00:00
verdict: FAIL_29AG_R2_TOPOLOGY_NOTES_VALUES_STATIC_PROOF_FAILED
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
full_live_replay_parity: NOT_PROVEN_IN_29AG_R2
repair_path: STATIC_PROOF_REPAIR_REQUIRED
next_batch: Repair topology notes values-preservation static/probe failure before guarded ReplayEngine retry.

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
- run/proofs/proof_topology_notes_values_preservation_repair_29ag_r2.json
- run/proofs/proof_topology_notes_values_preservation_repair_29ag_r2_latest.json
- run/proofs/batch29ag_r2_topology_notes_values_preservation_repair_20260502_121639_driver_proof.json
- etc/replay/parity/topology_notes_values_preservation_repair_29ag_r2.json
