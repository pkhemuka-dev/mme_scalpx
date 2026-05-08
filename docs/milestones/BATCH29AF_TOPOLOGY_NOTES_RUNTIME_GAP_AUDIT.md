BATCH 29AF TOPOLOGY NOTES RUNTIME GAP AUDIT

generated_at_utc: 2026-05-02T06:40:46.061214+00:00
verdict: PASS_TOPOLOGY_NOTES_RUNTIME_GAP_AUDIT_29AF
runtime_gap_kind: OFFLINE_REPLAY_TOPOLOGY_PLAN_NOTES_ATTRIBUTE_GAP
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'notes'
topology_notes_gap_confirmed: True
engine_consumes_notes: True
canonical_topology_notes_present: True
offline_topology_notes_present: False
repair_path: REPAIR_OFFLINE_TOPOLOGY_NOTES_ALIAS
next_batch: Batch 29AG — repair OfflineReplayTopologyPlan.notes alias in offline_context_shim.py only, then retry guarded ReplayEngine dry-run; still not paper/live enablement.

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
- run/proofs/proof_topology_notes_runtime_gap_audit_29af.json
- run/proofs/proof_topology_notes_runtime_gap_audit_29af_latest.json
- run/proofs/batch29af_topology_notes_runtime_gap_audit_20260502_121045_driver_proof.json
- etc/replay/parity/topology_notes_runtime_gap_audit_29af.json
