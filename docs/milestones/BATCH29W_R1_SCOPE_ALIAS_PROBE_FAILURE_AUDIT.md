BATCH 29W-R1 SCOPE ALIAS PROBE FAILURE AUDIT

generated_at_utc: 2026-05-02T05:49:25.135674+00:00
verdict: PASS_29W_R1_SCOPE_PROBE_FAILURE_CLASSIFIED
scope_alias_present: True
scope_probe_failure_kind: SCOPE_VALUE_MISMATCH_VALUES_SCOPE_NOT_PRESERVED
fresh_scope_probe_ok: False
fresh_scope_value_repr: 'offline_replay'
repair_path: REPAIR_OFFLINE_TOPOLOGY_PLAN_VALUES_SCOPE_PRESERVATION
next_batch: Batch 29W-R2 — repair OfflineReplayTopologyPlan scope alias to preserve provided values['scope'], still offline/replay only.

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
- run/proofs/proof_offline_topology_scope_alias_probe_failure_audit_29w_r1.json
- run/proofs/proof_offline_topology_scope_alias_probe_failure_audit_29w_r1_latest.json
- run/proofs/batch29w_r1_scope_alias_probe_failure_audit_20260502_111924_driver_proof.json
- etc/replay/parity/offline_topology_scope_alias_probe_failure_audit_29w_r1.json
