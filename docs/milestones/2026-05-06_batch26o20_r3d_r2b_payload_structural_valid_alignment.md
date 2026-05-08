# 2026-05-06 — Batch 26-O20-R3D-R2B Returned Payload structural_valid Alignment

## Status

R2A failed only due to returned payload mismatch:

- persisted samples were valid,
- HOLD-only safety held,
- only `feature_once_payload_structural_valid` was false.

## Scope

- Patch target: `app/mme_scalpx/services/features.py` only.
- No risk/execution patch.
- No paper start.
- No broker call.
- Real-live remains blocked.

## Proof

- `run/proofs/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.json`
- `run/proofs/manifest_batch26o20_r3d_r2b_payload_structural_valid_alignment.json`

## Next

If PASS:

- Batch 26-O20-R3E corrected bounded observation rerun.
- Still no real live.
