# Batch 29AI-R2 — Topology Fingerprint Actual Authority Repair

generated_at_utc: 2026-05-02T06:40:03.662641+00:00
verdict: `FAIL_TOPOLOGY_FINGERPRINT_ACTUAL_AUTHORITY_REPAIR_29AI_R2`
blockers: `['OFFLINE_REPLAY_TOPOLOGY_PLAN_NOT_EXPORTED', 'ACTUAL_SOURCE_FILE_NOT_LOCATED', 'ACTUAL_SOURCE_FILE_NOT_UNDER_REPLAY_PACKAGE', 'TOPOLOGY_FINGERPRINT_ALIAS_NOT_PRESENT_AFTER_PATCH', 'TOPOLOGY_FINGERPRINT_ALIAS_NOT_PROPERTY_AFTER_PATCH', 'IMPORT_TOPOLOGY_FINGERPRINT_PROBE_FAILED']`

## Scope

- located actual `OfflineReplayTopologyPlan` class authority by import introspection
- patched only the actual defining file if `topology_fingerprint` was missing
- no replay execution
- no broker IO
- no live Redis reads/writes
- no service start
- no order sending
- no paper/live enablement

## Authority

- source_file: `None`
- class_module: `None`

## Proofs

- proof: `run/proofs/proof_topology_fingerprint_actual_authority_repair_29ai_r2.json`
- latest: `run/proofs/proof_topology_fingerprint_actual_authority_repair_29ai_r2_latest.json`
- driver_proof: `run/proofs/batch29ai_r2_topology_fingerprint_actual_authority_repair_20260502_121003_driver_proof.json`
- config: `etc/replay/parity/topology_fingerprint_actual_authority_repair_29ai_r2.json`
- backup_dir: `run/_code_backups/batch29ai_r2_topology_fingerprint_actual_authority_repair_20260502_121003`

## Next

Batch 29AJ — bounded guarded replay dry-run retry after topology_fingerprint actual authority repair, still not paper/live enablement.
