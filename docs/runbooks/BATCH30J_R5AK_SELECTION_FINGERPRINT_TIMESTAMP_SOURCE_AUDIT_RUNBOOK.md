# Batch 30J-R5AK Runbook

Purpose:
Audit whether R5AJ same-dataset repeatability drift is caused by runtime timestamp fields entering selection/input fingerprints.

Proof:
`run/proofs/proof_batch30j_r5ak_selection_fingerprint_timestamp_source_audit_latest.json`

Artifact diff summaries:
`run/audits/batch30j_r5ak_selection_fingerprint_timestamp_source_audit_20260510_101621/artifact_diff_summaries.json`

Source scans:
`run/audits/batch30j_r5ak_selection_fingerprint_timestamp_source_audit_20260510_101621/source_scans.json`

Patch candidates:
`run/audits/batch30j_r5ak_selection_fingerprint_timestamp_source_audit_20260510_101621/patch_candidates.json`

Next:
Write minimal patch to exclude volatile timestamp fields from selection/input fingerprint surfaces, then compile/import and rerun same-dataset repeatability.
