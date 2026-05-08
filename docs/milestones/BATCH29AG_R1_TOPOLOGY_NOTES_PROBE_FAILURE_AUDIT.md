BATCH 29AG-R1 TOPOLOGY NOTES PROBE FAILURE AUDIT

generated_at_utc: 2026-05-02T06:44:56.436954+00:00
verdict: PASS_29AG_R1_TOPOLOGY_NOTES_PROBE_FAILURE_CLASSIFIED
notes_probe_failure_kind: VALUES_NOTES_NOT_PRESERVED
fresh_notes_probe_ok: False
fresh_notes1_repr: ()
fresh_notes2_repr: ()
fresh_top_error: None
repair_path: REPAIR_TOPOLOGY_NOTES_VALUES_PRESERVATION
next_batch: Batch 29AG-R2 — repair OfflineReplayTopologyPlan.notes to read/coerce values['notes'] before metadata/source fallback.

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
- run/proofs/proof_topology_notes_probe_failure_audit_29ag_r1.json
- run/proofs/proof_topology_notes_probe_failure_audit_29ag_r1_latest.json
- run/proofs/batch29ag_r1_topology_notes_probe_failure_audit_20260502_121456_driver_proof.json
- etc/replay/parity/topology_notes_probe_failure_audit_29ag_r1.json
