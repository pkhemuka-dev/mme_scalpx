# Batch 26-OI-A — Dhan/OI Option Context Surface Audit

Date: 2026-04-29
Revision: R2

## Verdict

`final_verdict = PASS_WITH_SURFACE_DRIFT_FINDING`

This batch was audit/proof only.

No live trading behavior was changed.
No hard OI filter was added.
No family doctrine was rewritten.
No strategy promotion was enabled.
No order-intent publication was enabled.
No risk/execution path was changed.

## Key Results

- Dhan ladder producer found: `True`
- Dhan ladder normalizer found: `True`
- Canonical OI wall authority: `app/mme_scalpx/services/feature_family/strike_selection.py`
- Duplicate wall logic detected: `True`
- OI used as immediate trigger detected: `False`
- MISO chain/live separation OK: `True`
- MISR registered-zone law OK: `True`
- Strategy HOLD-only OK: `True`
- Live order bypass detected: `False`

## Blocking Failures

- None.

## Surface Drift Finding

The audit confirms `strike_selection.py` is the declared canonical OI wall authority, but wall/fallback calculations also exist in producer/feature paths.

- `app/mme_scalpx/services/feeds.py`: producer-side Dhan ladder / wall summary construction at lines [986, 1096, 1196] (producer-side preliminary context)
- `app/mme_scalpx/services/features.py`: features fallback nearest-wall calculation at lines [2088, 2089, 2139] (fallback wall logic)
- `app/mme_scalpx/services/feature_family/strike_selection.py`: build_oi_wall_summary at lines [185, 856, 1011, 1050, 1104, 1135, 1171] (declared canonical authority)

This is a surface-drift finding, not a live-order bypass.

## Required Proof Artifact

- `run/proofs/proof_oi_context_surface_audit.json`

## Recommended Next Batch

Batch 26-OI-B — canonicalize OI wall authority so strike_selection.py is the sole wall calculator and features.py only publishes canonical context. Preserve HOLD/report-only safety.
