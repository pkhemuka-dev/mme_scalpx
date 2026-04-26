# Batch 25K-C — Shared Builder ABI Proof Import-Root Corrective

Date: 2026-04-26
Timestamp: 20260426_132425

## Objective

Repair Batch 25K proof execution after the shared-builder ABI patch compiled and import-checked successfully, but direct proof execution failed.

## Root Cause

`bin/proof_feature_family_shared_builder_abi.py` was executed directly from `bin/` and imported `app.mme_scalpx...` before adding the repository root to `sys.path`.

Failure:

```text
ModuleNotFoundError: No module named 'app'
```

## Files Patched

- `bin/proof_feature_family_shared_builder_abi.py`

## Files Verified

- `app/mme_scalpx/services/features.py`
- `app/mme_scalpx/services/feature_family/futures_core.py`
- `app/mme_scalpx/services/feature_family/option_core.py`
- `app/mme_scalpx/services/feature_family/regime.py`
- `app/mme_scalpx/services/feature_family/tradability.py`
- `app/mme_scalpx/services/feature_family/strike_selection.py`

## Proof

Proof artifact:

```text
run/proofs/proof_feature_family_shared_builder_abi.json
```

Required result:

```json
"feature_family_shared_builder_abi_ok": true
```

## Runtime Safety

This corrective patch does not change feed ingestion, provider failover, Dhan OI persistence, strategy promotion, risk, or execution arming.

`observe_only` remains default.

## Remaining Outside This Batch

- Batch 25L: family branch/root surface wiring repair
- Batch 25M: canonical family_features support alias and eligibility repair
- Batch 25N: MISO provider doctrine alignment
- Batch 25O: strategy-family reverse requirement coverage proof

## Verdict

Batch 25K is freeze-final only after:

```text
feature_family_shared_builder_abi_ok = True
proof_secret_scan_ok = True
```
