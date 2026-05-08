BATCH 29W OFFLINE TOPOLOGY SCOPE ALIAS REPAIR

generated_at_utc: 2026-05-02T05:48:02.427802+00:00
verdict: FAIL_29W_SCOPE_ALIAS_STATIC_PROOF_FAILED
patch_applied: True
scope_alias_present: True
scope_probe_ok: False
topology_scope_gap_resolved: False
retry_returncode: None
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'scope'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29W
repair_path: STATIC_PROOF_REPAIR_REQUIRED
next_batch: Repair scope alias static/probe failure before guarded ReplayEngine retry.

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
- run/proofs/proof_offline_topology_scope_alias_repair_29w.json
- run/proofs/proof_offline_topology_scope_alias_repair_29w_latest.json
- run/proofs/batch29w_offline_topology_scope_alias_repair_20260502_111801_driver_proof.json
- etc/replay/parity/offline_topology_scope_alias_repair_29w.json
