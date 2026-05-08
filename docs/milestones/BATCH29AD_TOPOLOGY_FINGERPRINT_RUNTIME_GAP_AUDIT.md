BATCH 29AD TOPOLOGY_FINGERPRINT RUNTIME GAP AUDIT

generated_at_utc: 2026-05-02T06:37:02.595675+00:00
verdict: PASS_TOPOLOGY_FINGERPRINT_RUNTIME_GAP_AUDIT_29AD
runtime_gap_kind: OFFLINE_REPLAY_TOPOLOGY_PLAN_TOPOLOGY_FINGERPRINT_ATTRIBUTE_GAP
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'topology_fingerprint'
topology_fingerprint_gap_confirmed: True
engine_consumes_topology_fingerprint: False
canonical_topology_fingerprint_present: True
offline_topology_fingerprint_present: False
repair_path: REPAIR_OFFLINE_TOPOLOGY_FINGERPRINT_ALIAS
next_batch: Batch 29AE — repair OfflineReplayTopologyPlan.topology_fingerprint alias in offline_context_shim.py only, then retry guarded ReplayEngine dry-run; still not paper/live enablement.

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
- run/proofs/proof_topology_fingerprint_runtime_gap_audit_29ad.json
- run/proofs/proof_topology_fingerprint_runtime_gap_audit_29ad_latest.json
- run/proofs/batch29ad_topology_fingerprint_runtime_gap_audit_20260502_120702_driver_proof.json
- etc/replay/parity/topology_fingerprint_runtime_gap_audit_29ad.json
