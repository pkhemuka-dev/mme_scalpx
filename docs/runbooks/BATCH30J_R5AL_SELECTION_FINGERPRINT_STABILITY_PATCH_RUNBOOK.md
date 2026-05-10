# Batch 30J-R5AL Runbook

Purpose:
Patch selection fingerprint computation so runtime-only timestamp/path/run fields do not affect fingerprint stability.

Proof:
`run/proofs/proof_batch30j_r5al_selection_fingerprint_stability_patch_latest.json`

Backup dir:
`run/_code_backups/batch30j_r5al_selection_fingerprint_stability_patch_20260510_103800`

Diff:
`run/audits/batch30j_r5al_selection_fingerprint_stability_patch_20260510_103800/selection_fingerprint_stability_patch.diff`

Next:
Rerun same-dataset-id repeatability to prove final single-date reproducibility.
