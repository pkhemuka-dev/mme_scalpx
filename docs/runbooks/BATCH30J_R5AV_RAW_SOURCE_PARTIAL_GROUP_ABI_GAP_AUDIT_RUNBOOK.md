# Batch 30J-R5AV Runbook

Purpose:
Inspect R5AU partial raw tick groups against replay repository ABI and locate missing surfaces or transform paths before materialization.

Proof:
`run/proofs/proof_batch30j_r5av_raw_source_partial_group_abi_gap_audit_latest.json`

Accepted 2026-04-18 raw sources:
`run/audits/batch30j_r5av_raw_source_partial_group_abi_gap_audit_20260510_113946/accepted_20260418_sources.json`

Existing replay tree:
`run/audits/batch30j_r5av_raw_source_partial_group_abi_gap_audit_20260510_113946/existing_replay_tree.json`

Nearby surface search:
`run/audits/batch30j_r5av_raw_source_partial_group_abi_gap_audit_20260510_113946/surface_search_near_raw_sources.json`

Transform candidates:
`run/audits/batch30j_r5av_raw_source_partial_group_abi_gap_audit_20260510_113946/transform_code_candidates.json`

Source scans:
`run/audits/batch30j_r5av_raw_source_partial_group_abi_gap_audit_20260510_113946/source_scans.json`

Next:
Do not materialize. Locate real replay-ready surfaces or implement a guarded raw-to-replay transform contract.
