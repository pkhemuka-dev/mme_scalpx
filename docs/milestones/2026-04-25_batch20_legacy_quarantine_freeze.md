# Batch 20 — Legacy Residue and Quarantine Freeze

## Scope

- `app/mme_scalpx/main.py`
- `app/mme_scalpx/services/features_legacy_single.py`
- `app/mme_scalpx/services/strategy_legacy_single.py`
- `etc/config_registry.yaml`
- `docs/contracts/compatibility_alias_registry.md`
- `docs/systemd_runtime_unit_registry.md`
- `bin/proof_repo_hygiene_quarantine.py`
- `bin/proof_legacy_baseline_quarantine.py`
- `bin/proof_names_alias_lifecycle.py`

## Decision

Legacy baseline is preserved as read-only reference/replay/shadow/rollback evidence.

Legacy baseline is not a canonical runtime service.

## Runtime law

- canonical runtime service registry must not include legacy modules;
- `main.py` forbidden runtime paths include both module-form and path-form entries:
  - `app.mme_scalpx.services.features_legacy_single`
  - `app.mme_scalpx.services.strategy_legacy_single`
  - `app/mme_scalpx/services/features_legacy_single.py`
  - `app/mme_scalpx/services/strategy_legacy_single.py`
- legacy modules may retain historical `run(context)` shape only because they are explicitly quarantined;
- legacy modules may import for proof/replay only;
- legacy modules must not directly write Redis, call broker execution, or publish live decisions.

## Alias lifecycle correction

`STATE_FEATURES` registry target was corrected to the actual canonical symbol present in `core/names.py`, instead of stale `HASH_FEATURES`.

## Proofs

Proof artifacts:

- `run/proofs/repo_hygiene_quarantine.json`
- `run/proofs/legacy_baseline_quarantine.json`
- `run/proofs/names_alias_lifecycle.json`

## Final proof result

Batch 20 is freeze-final when all three proof JSON files show `"status": "PASS"` and compile/import proof passes.
