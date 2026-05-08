# Batch 30J-R5K Runbook

Purpose:
Locate exact source assignment that writes integrity `verdict='fail'` despite zero failed checks.

Proof:
`run/proofs/proof_batch30j_r5k_integrity_verdict_source_locator_latest.json`

Candidate targets:
`run/audits/batch30j_r5k_integrity_verdict_source_locator_20260508_150822/candidate_targets.json`

Source scans:
`run/audits/batch30j_r5k_integrity_verdict_source_locator_20260508_150822/source_scans.json`

Next:
Inspect artifact writer/runtime object serialization path; no patch.
