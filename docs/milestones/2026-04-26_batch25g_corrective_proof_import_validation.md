# Batch 25G-C — Contract Field Registry Corrective Proof Repair

Date: 2026-04-26
Timestamp: 20260426_130342

## Objective

Repair Batch 25G proof execution and validation coverage without starting Batch 25H runtime behavior work.

## Root Cause

Batch 25G wrote `bin/proof_contract_field_registry.py` with direct `app.mme_scalpx...` imports and then executed the script directly from `bin/`.

Direct script execution made Python resolve imports from `bin/` first, causing:

```text
ModuleNotFoundError: No module named 'app'
```

## Files Patched

- `bin/proof_contract_field_registry.py`
- `app/mme_scalpx/core/models.py`

## Fixes

- Added repo-root bootstrap inside `bin/proof_contract_field_registry.py`
- Preserved direct script execution compatibility
- Added explicit alias-aware provider-runtime model coverage proof
- Preserved canonical provider-runtime field registry as frozen truth
- Marked canonical provider-runtime producer/consumer readiness as Batch 25H scope
- Repaired possible Dhan OI/context JSON validation-list gap in:
  - `DhanContextEvent`
  - `DhanContextState`

## Proof

Proof artifact:

```text
run/proofs/proof_contract_field_registry.json
```

Required freeze condition:

```json
"contract_field_registry_ok": true
```

## Runtime Safety

This corrective patch does not enable strategy promotion.

This corrective patch does not arm execution.

This corrective patch does not modify Redis reads/writes.

This corrective patch does not change live service loops.

`observe_only` remains the default doctrine posture.

## Remaining Outside This Batch

- Batch 25H: provider runtime producer/consumer repair
- Batch 25I: feed snapshot to feature raw-surface adapter
- Batch 25J: Dhan OI ladder and option-chain persistence
- Batch 25K onward: feature-family builder ABI, family support aliases, strategy candidate metadata, disabled promotion adapter, risk/execution seam proof

## Verdict

Batch 25G is freeze-final only after `run/proofs/proof_contract_field_registry.json` reports:

```json
"contract_field_registry_ok": true
```
