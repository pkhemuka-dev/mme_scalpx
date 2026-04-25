# Batch 7 — Feeds/Features Corrective Freeze Final

Date: 2026-04-25 10:53:33 IST

## Corrective scope

Files:

- `app/mme_scalpx/services/feeds.py`
- `app/mme_scalpx/services/features.py`
- `bin/proof_feeds_features_batch7_freeze.py`

## Problems fixed

The first Batch 7 proof run failed two cases:

1. `strict_dual_marketdata_adapters_accepted`
   - Cause: hardening wrapper broke original `_extract_adapter_surfaces()` tuple return contract.
   - Fix: restore contract-safe return shape:
     `tuple[dict[str, ProviderAdapterSurface], Mapping[str, Any]]`.

2. `sync_span_above_threshold_invalidates_snapshot`
   - Cause: `_snapshot_block()` collapsed futures and selected-option timestamps into one active timestamp.
   - Fix: compute `futures_snapshot_ns`, `selected_option_snapshot_ns`, `fut_opt_skew_ms`, `sync_ok`, and `valid` from member-level timestamps.

## Result required

Batch 7 feeds/features is freeze-final if:

- compile proof passes
- import/surface proof passes
- `bin/proof_feeds_features_batch7_freeze.py` returns status PASS
- strict Redis contract regression remains PASS
- prior batch regression smoke remains PASS where scripts exist

## Proof artifact

- `run/proofs/feeds_features_batch7_freeze.json`

## Boundary

This closes the feeds/features false-readiness batch only. It does not close:

- whole-tree replay/dataset.py P0 indentation error
- real-live Dhan/Zerodha adapter synchronization proof
- Dhan execution fallback implementation/quarantine
- live MISO promotion proof

