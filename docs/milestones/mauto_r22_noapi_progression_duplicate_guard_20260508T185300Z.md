# MAUTO-R2.2 — Progression / Duplicate Batch Guard

## Purpose

- Fix A14 -> A15 progression.
- Stop mauto if selected/generated batch differs from latest proof expected batch.
- Add robust top-level fallback extraction for A14 proof fields.
- Prevent duplicate A14 execution when latest proof requires A15.

## Safety

- Generated script was not executed by this repair.
- No service start.
- No broker call.
- No live Redis write.
- No paper/live enablement.

## Proof

- `run/proofs/proof_mauto_r22_noapi_progression_duplicate_guard_20260508T185300Z.json`
