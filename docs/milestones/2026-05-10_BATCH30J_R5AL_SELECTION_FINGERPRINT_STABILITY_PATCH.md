# Batch 30J-R5AL — Selection Fingerprint Stability Patch

Verdict: `PASS_PATCH_APPLIED_SAFE_VALIDATION_OK`
Classification: `SELECTION_FINGERPRINT_EXCLUDES_VOLATILE_RUNTIME_FIELDS`

Target:
`app/mme_scalpx/replay/selectors.py`

Changed files:
[
  {
    "path": "app/mme_scalpx/replay/selectors.py",
    "sha256_before": "40e832b12b1238b2f90770680b3b932b4b31ddbdae20db8cc4f82bdb760bdf4c",
    "sha256_after": "54daaac08994042538a8ad2764df8b408fd714182f158c4c1c4dfa520a760c29"
  }
]

Patch notes:
[
  "Inserted fingerprint-only volatile runtime field stripper before ReplaySelector.",
  "Selection fingerprint now hashes a copy stripped of volatile runtime fields."
]

No replay execution.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Rerun same-dataset-id repeatability to prove final single-date reproducibility.
