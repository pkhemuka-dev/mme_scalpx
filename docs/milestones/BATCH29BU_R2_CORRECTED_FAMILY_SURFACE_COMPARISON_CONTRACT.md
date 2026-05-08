# Batch 29BU-R2 — Corrected Family Surface Comparison Contract

- Generated UTC: 2026-05-03T10:37:28.159485+00:00
- Dataset: observe_only_replay_input_9c50b37fb4782fb0
- Source R1 proof: run/proofs/proof_family_surface_mismatch_review_29bu_r1_latest.json
- Source R1 loaded: True
- Source R1 expected overstrict-rich-surface status: True
- Contract: etc/replay/parity/family_surface_comparison_contract_29bu_r2.json
- Contract latest: etc/replay/parity/family_surface_comparison_contract_latest.json
- Corrected contract frozen: True
- Verdict: PASS_29BU_R2_CORRECTED_FAMILY_SURFACE_COMPARISON_CONTRACT_FROZEN_REPLAY_ONLY

## Scope

- Replay/parity comparison contract only.
- No production doctrine change.
- No production code patch.
- No broker call.
- No live Redis write.
- No paper_armed approval.
- No live trading approval.

## Contract conclusion

Rich-surface status-only fields are not strategy doctrine parity facts and must be classified as NOT_COMPARABLE.
Canonical doctrine fields, provider readiness fields, and event identity fields remain strict comparable fields.

## Next

Batch 29BU-R3 — apply corrected comparison contract to 29BU-R1 mismatch evidence and prove rich-surface-status-only mismatches reclassify as NOT_COMPARABLE while canonical doctrine fields remain strict.
