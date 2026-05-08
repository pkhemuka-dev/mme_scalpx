# Batch 29AI — Topology Fingerprint Alias Repair

generated_at_utc: 2026-05-02T06:38:46.277335+00:00
verdict: `FAIL_TOPOLOGY_FINGERPRINT_ALIAS_REPAIR_29AI`
blockers: `['TOPOLOGY_FINGERPRINT_ALIAS_NOT_PRESENT_AFTER_PATCH', 'TOPOLOGY_FINGERPRINT_ALIAS_NOT_PROPERTY_AFTER_PATCH', 'IMPORT_TOPOLOGY_FINGERPRINT_PROBE_FAILED']`

## Scope

- patched only `app/mme_scalpx/replay/topology.py` if `OfflineReplayTopologyPlan.topology_fingerprint` was missing
- no replay execution
- no broker IO
- no live Redis reads/writes
- no service start
- no order sending
- no paper/live enablement

## Proofs

- proof: `run/proofs/proof_topology_fingerprint_alias_repair_29ai.json`
- latest: `run/proofs/proof_topology_fingerprint_alias_repair_29ai_latest.json`
- driver_proof: `run/proofs/batch29ai_topology_fingerprint_alias_repair_20260502_120846_driver_proof.json`
- config: `etc/replay/parity/topology_fingerprint_alias_repair_29ai.json`
- backup_dir: `run/_code_backups/batch29ai_topology_fingerprint_alias_repair_20260502_120846`

## Next

Batch 29AJ — bounded guarded replay dry-run retry after topology_fingerprint alias repair, still not paper/live enablement.
