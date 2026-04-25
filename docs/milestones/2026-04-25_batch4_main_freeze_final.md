# Batch 4 — main.py Freeze Final

Date: 2026-04-25 10:17:08 IST

## Scope

`app/mme_scalpx/main.py` canonical composition root.

## Result required

Batch 4 is freeze-final if:

- `app/mme_scalpx/main.py` compiles.
- `bin/proof_main_batch4_freeze.py` returns status PASS.
- strict Redis contract regression remains PASS.
- prior Batch 2/3 proof smoke remains PASS where scripts exist.

## Fixes applied

- Added strict provider runtime flag:
  - `MME_PROVIDER_RUNTIME_STRICT`
- Added explicit legacy provider alias flag:
  - `MME_ALLOW_LEGACY_PROVIDER_ALIAS`
- Prevented silent legacy feed adapter inference in strict provider mode.
- Split market-data adapter checks from context-only adapter checks.
- Made feeds dependency require true market-data adapter.
- Ensured `dhan_context_adapter` alone does not satisfy feeds dependency.
- Added strict dual-provider surface validation:
  - `zerodha_feed_adapter`
  - `dhan_feed_adapter`
  - `feed_adapters[ZERODHA]`
  - `feed_adapters[DHAN]`
- Explicitly quarantined:
  - `app.mme_scalpx.services.features_legacy_single`
  - `app.mme_scalpx.services.strategy_legacy_single`
- Added effective runtime truth report to doctor output without changing runtime behavior.
- Kept `runtime.yaml` observational only in Batch 4.
- Preserved `main.py` as the only composition root.

## Explicit non-change

Batch 4 does not silently make `runtime.yaml` authoritative and does not silently change runtime mode behavior.

Current runtime source remains:

- settings.py / MME_* environment
- CLI flags
- explicit bootstrap provider

`runtime.yaml` is now reported for proof visibility only.

## Proof artifact

- `run/proofs/main_batch4_freeze.json`

## Remaining outside Batch 4

Whole-tree freeze remains blocked by:

- `app/mme_scalpx/replay/dataset.py`
- `IndentationError: unexpected indent around line 786`

Next batch remains:

- Batch 5 provider/broker integration layer
- provider_runtime / Dhan / Zerodha adapter truth
- MISO/Dhan-context promotion disable/degrade proof

