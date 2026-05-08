# Batch 30J-R5X Runbook

Purpose:
Audit whether replay feature rows can safely promote metadata.source_file/source_stem to top-level parity fields.

Proof:
`run/proofs/proof_batch30j_r5x_feature_source_surface_audit_latest.json`

Feature row analysis:
`run/audits/batch30j_r5x_feature_source_surface_audit_20260508_152928/feature_row_analysis.json`

Likely patch surfaces:
`run/audits/batch30j_r5x_feature_source_surface_audit_20260508_152928/likely_patch_surfaces.json`

Next:
Write exact minimal patch to promote metadata.source_file/source_stem to top-level features_rows fields; compile/import only.
