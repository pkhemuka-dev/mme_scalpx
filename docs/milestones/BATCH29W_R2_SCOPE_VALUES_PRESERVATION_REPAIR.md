BATCH 29W-R2 SCOPE VALUES PRESERVATION REPAIR

generated_at_utc: 2026-05-02T05:57:59.677620+00:00
verdict: DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_SCOPE_VALUES_REPAIR_29W_R2
patch_applied: False
scope_values_preserved: True
scope_probe_ok: True
topology_scope_gap_resolved: True
retry_returncode: 2
retry_runtime_error: AttributeError: 'str' object has no attribute 'value'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29W_R2
repair_path: NEXT_REPLAY_ENGINE_RUNTIME_GAP_AUDIT
next_batch: Batch 29X — audit/classify next guarded ReplayEngine runtime gap after scope values repair, still not paper/live enablement.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- none

Proofs:
- run/proofs/proof_offline_topology_scope_values_preservation_repair_29w_r2.json
- run/proofs/proof_offline_topology_scope_values_preservation_repair_29w_r2_latest.json
- run/proofs/batch29w_r2_scope_values_preservation_repair_20260502_112758_driver_proof.json
- etc/replay/parity/offline_topology_scope_values_preservation_repair_29w_r2.json
