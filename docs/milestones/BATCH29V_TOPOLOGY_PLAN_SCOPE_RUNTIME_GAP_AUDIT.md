BATCH 29V TOPOLOGY PLAN SCOPE RUNTIME GAP AUDIT

generated_at_utc: 2026-05-02T05:46:12.930410+00:00
verdict: PASS_TOPOLOGY_PLAN_SCOPE_RUNTIME_GAP_AUDIT_29V
runtime_gap_kind: OFFLINE_REPLAY_TOPOLOGY_PLAN_SCOPE_ATTRIBUTE_GAP
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'scope'
topology_scope_gap_confirmed: True
engine_consumes_topology_scope: False
canonical_topology_scope_present: True
offline_topology_scope_present: False
repair_path: REPAIR_OFFLINE_TOPOLOGY_PLAN_SCOPE_ALIAS
next_batch: Batch 29W — repair OfflineReplayTopologyPlan.scope alias in offline_context_shim.py only if current evidence still matches, still not paper/live enablement.

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
- run/proofs/proof_topology_plan_scope_runtime_gap_audit_29v.json
- run/proofs/proof_topology_plan_scope_runtime_gap_audit_29v_latest.json
- run/proofs/batch29v_topology_plan_scope_runtime_gap_audit_20260502_111612_driver_proof.json
- etc/replay/parity/topology_plan_scope_runtime_gap_audit_29v.json
