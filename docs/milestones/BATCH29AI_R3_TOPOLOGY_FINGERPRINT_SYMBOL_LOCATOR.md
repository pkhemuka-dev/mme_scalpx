# Batch 29AI-R3 — Topology Fingerprint Symbol Locator

generated_at_utc: 2026-05-02T06:41:22.870510+00:00
verdict: `PASS_TOPOLOGY_FINGERPRINT_SYMBOL_LOCATOR_29AI_R3`
blockers: `['LOCATOR_ONLY_REPAIR_NOT_APPLIED_IN_29AI_R3']`
classified_locator_kind: `EXACT_CLASS_DEFINITION_LOCATED`

## Scope

- locate actual `OfflineReplayTopologyPlan` / `topology_fingerprint` symbol and callsites
- no code patch
- no replay rerun
- no broker IO
- no live Redis reads/writes
- no service start
- no order sending
- no paper/live enablement

## Locator result

- exact_class_definitions: `1`
- topology_like_classes: `4`
- callsite_hits: `13`

## Proofs

- proof: `run/proofs/proof_topology_fingerprint_symbol_locator_29ai_r3.json`
- latest: `run/proofs/proof_topology_fingerprint_symbol_locator_29ai_r3_latest.json`
- driver_proof: `run/proofs/batch29ai_r3_topology_fingerprint_symbol_locator_20260502_121122_driver_proof.json`
- config: `etc/replay/parity/topology_fingerprint_symbol_locator_29ai_r3.json`
- backup_dir: `run/_code_backups/batch29ai_r3_topology_fingerprint_symbol_locator_20260502_121122`

## Next

Batch 29AI-R4 — patch topology_fingerprint in located exact class authority only.
