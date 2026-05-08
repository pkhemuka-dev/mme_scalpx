BATCH 29Y-R1 SCOPE VALUE PROBE FAILURE AUDIT

generated_at_utc: 2026-05-02T06:06:04.930718+00:00
verdict: PASS_29Y_R1_SCOPE_VALUE_PROBE_FAILURE_CLASSIFIED
scope_value_probe_failure_kind: PLAN_CONSTRUCTION_OR_SCOPE_PROPERTY_EXCEPTION
fresh_scope_value_probe_ok: False
fresh_scope_type: None
fresh_scope_value_repr: None
fresh_scope_dot_value_repr: None
repair_path: REPAIR_SCOPE_VALUE_PROPERTY_EXCEPTION
next_batch: Batch 29Y-R2 — repair OfflineReplayTopologyPlan.scope value compatibility exception, still offline/replay only.

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
- run/proofs/proof_scope_value_probe_failure_audit_29y_r1.json
- run/proofs/proof_scope_value_probe_failure_audit_29y_r1_latest.json
- run/proofs/batch29y_r1_scope_value_probe_failure_audit_20260502_113604_driver_proof.json
- etc/replay/parity/scope_value_probe_failure_audit_29y_r1.json
