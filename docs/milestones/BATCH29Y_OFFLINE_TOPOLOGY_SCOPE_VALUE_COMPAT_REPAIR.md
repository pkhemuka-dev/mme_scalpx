BATCH 29Y OFFLINE TOPOLOGY SCOPE VALUE COMPAT REPAIR

generated_at_utc: 2026-05-02T06:03:09.262834+00:00
verdict: FAIL_29Y_SCOPE_VALUE_COMPAT_STATIC_PROOF_FAILED
patch_applied: True
scope_value_compat_present: True
scope_value_probe_ok: False
scope_value_gap_resolved: False
retry_returncode: None
retry_runtime_error: AttributeError: 'str' object has no attribute 'value'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29Y
repair_path: STATIC_PROOF_REPAIR_REQUIRED
next_batch: Repair scope .value static/probe failure before guarded ReplayEngine retry.

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
- run/proofs/proof_offline_topology_scope_value_compat_repair_29y.json
- run/proofs/proof_offline_topology_scope_value_compat_repair_29y_latest.json
- run/proofs/batch29y_offline_topology_scope_value_compat_repair_20260502_113308_driver_proof.json
- etc/replay/parity/offline_topology_scope_value_compat_repair_29y.json
