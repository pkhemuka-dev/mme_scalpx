BATCH 29X TOPOLOGY SCOPE VALUE RUNTIME GAP AUDIT

generated_at_utc: 2026-05-02T05:59:16.489810+00:00
verdict: PASS_TOPOLOGY_SCOPE_VALUE_RUNTIME_GAP_AUDIT_29X
runtime_gap_kind: OFFLINE_REPLAY_TOPOLOGY_SCOPE_VALUE_ATTRIBUTE_GAP
retry_runtime_error: AttributeError: 'str' object has no attribute 'value'
scope_value_gap_confirmed: True
scope_values_preserved: True
topology_scope_gap_resolved: True
repair_path: REPAIR_OFFLINE_TOPOLOGY_SCOPE_VALUE_COMPATIBILITY
next_batch: Batch 29Y — repair OfflineReplayTopologyPlan.scope to provide .value-compatible offline scope object, still not paper/live enablement.

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
- run/proofs/proof_topology_scope_value_runtime_gap_audit_29x.json
- run/proofs/proof_topology_scope_value_runtime_gap_audit_29x_latest.json
- run/proofs/batch29x_topology_scope_value_runtime_gap_audit_20260502_112916_driver_proof.json
- etc/replay/parity/topology_scope_value_runtime_gap_audit_29x.json
