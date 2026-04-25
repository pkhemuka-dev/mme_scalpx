# Batch 2 — core/models.py Freeze Final

Date: 2026-04-25 01:24:52 IST

## Scope

Surgical hardening of `app/mme_scalpx/core/models.py` after Batch 2 line-by-line audit.

## Result required

Batch 2 is freeze-final if:

- `app/mme_scalpx/core/models.py` compiles.
- `bin/proof_models_batch2_freeze.py` returns status PASS.
- Required Batch 2 models are exported and registered:
  - `ProviderInstrumentRef`
  - `StrategyFamilyCandidate`
  - `StrategyOrderIntent`
  - `EffectiveRuntimeConfigState`
- Strict Redis matrix regression remains PASS.

## Fixes applied

- Added strict promoted `StrategyOrderIntent` bridge.
- Added `StrategyOrderIntent.to_execution_metadata()`.
- Added `StrategyOrderIntent.to_strategy_decision_payload()`.
- Added `StrategyOrderIntent.to_strategy_decision()`.
- Added canonical `StrategyFamilyCandidate`.
- Added provider instrument equivalence model `ProviderInstrumentRef`.
- Added Dhan selected option symbol/token/security-id/zerodha-token fields.
- Added provider transition safety fields.
- Added execution provider route truth fields.
- Added `EffectiveRuntimeConfigState` for runtime-proof bundles.
- Registered/exported new models.

## Proof artifact

- `run/proofs/models_batch2_freeze.json`

## Remaining outside Batch 2

Whole-tree freeze remains blocked by the known replay compile issue:

- `app/mme_scalpx/replay/dataset.py`
- `IndentationError: unexpected indent at line 786`

Core infrastructure gaps from Batch 3 remain separate:

- `codec.py` postponed-annotation hash/event helper bug.
- `redisx.py` typed stream helper decode seam.
- runtime config truth mismatch pending main.py audit.

