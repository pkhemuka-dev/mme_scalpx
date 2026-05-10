# Batch 30J-R5AI — Selection Fingerprint Mismatch Source Audit

Verdict: `PASS_CLASSIFIED_DATASET_ID_INDUCED_SELECTION_FINGERPRINT_DRIFT`
Classification: `REPLAY_OUTPUTS_REPEATABLE_BUT_TEST_USED_DIFFERENT_DATASET_IDS`

R5AG stage outputs equal from prior stable comparison:
`True`

Artifact stage outputs equal after normalization:
`True`

Integrity-only selection fingerprint diff:
`True`

Command dataset-id differs:
`True`

No replay execution.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Rerun repeatability with identical dataset-id for A/B to prove final single-date reproducibility.
