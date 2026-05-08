# 2026-05-05 — Batch 26-O20-R3A Persistent Features ABI Publish Repair

## Status

O20-R3 failed because persistent features service published invalid ABI after service start.

## Scope

- Patch target: `app/mme_scalpx/services/features.py` only.
- No strategy/risk/execution patch.
- No paper start.
- No broker call.
- Real-live remains blocked.

## Proof

- `run/proofs/proof_batch26o20_r3a_persistent_features_abi_publish_repair.json`
- `run/proofs/manifest_batch26o20_r3a_persistent_features_abi_publish_repair.json`

## Next

If PASS:

- Batch 26-O20-R3B corrected bounded observation rerun.
