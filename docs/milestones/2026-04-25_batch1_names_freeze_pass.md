# Batch 1 — names.py Institutional Hardening Freeze Pass

Date: 2026-04-25 01:13:48 IST

## Scope

Batch 1 covered `app/mme_scalpx/core/names.py` and direct institutional hardening around the names contract.

## Result

Batch 1 is freeze-pass if the following proofs passed in this run:

- `N.validate_names_contract()`
- `N.validate_names_hardening_contract()`
- `ops/bootstrap_groups.py --dry-run`
- `ops/bootstrap_groups.py --dry-run --replay`
- `bin/proof_names_hardening.py`
- `bin/proof_redis_contract_matrix.py`

## Final corrections applied

- Standalone script import path fixed for direct file execution.
- `ops/bootstrap_groups.py` consumes `names.get_group_specs()`.
- Proof scanners now exclude archived audit bundles under `run/audit_bundle_*`.
- Proof scanners no longer self-flag their own stale-literal definitions.
- Live `features.py` stale Redis fallback literals were removed or canonicalized to `names.py` symbols.

## Proof artifacts

- `run/proofs/names_institutional_hardening.json`
- `run/proofs/redis_contract_matrix.json`

## Remaining outside Batch 1

Whole-tree freeze remains blocked by the known replay compile issue:

- `app/mme_scalpx/replay/dataset.py`
- `IndentationError: unexpected indent at line 786`

