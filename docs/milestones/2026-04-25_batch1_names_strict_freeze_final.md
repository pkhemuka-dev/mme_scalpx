# Batch 1 — names.py Strict Institutional Freeze Final

Date: 2026-04-25 01:16:39 IST

## Scope

Strict closure of Batch 1 names.py institutional hardening.

## Final result required

- `N.validate_names_contract()`: PASS
- `N.validate_names_hardening_contract()`: PASS
- `ops/bootstrap_groups.py --dry-run`: PASS
- `ops/bootstrap_groups.py --dry-run --replay`: PASS
- `bin/proof_names_hardening.py`: PASS
- `bin/proof_redis_contract_matrix.py`: PASS
- `bin/proof_redis_contract_matrix.py --strict-raw`: PASS

## Final strict cleanup

Raw canonical Redis literals outside `core/names.py` were canonicalized to `N.*` symbols in:

- `app/mme_scalpx/services/strategy.py`
- `app/mme_scalpx/services/features.py`
- `bin/proof_strategy_hold_bridge_offline.py`
- `bin/proof_strategy_family_consumer_offline.py`
- `bin/proof_family_features_offline.py`
- `bin/proof_strategy_family_compat_offline.py`
- `bin/export_session_artifacts.py`

## Proof artifacts

- `run/proofs/names_institutional_hardening.json`
- `run/proofs/redis_contract_matrix.json`

## Remaining outside Batch 1

Whole-tree freeze remains blocked by the known replay compile issue:

- `app/mme_scalpx/replay/dataset.py`
- `IndentationError: unexpected indent at line 786`

