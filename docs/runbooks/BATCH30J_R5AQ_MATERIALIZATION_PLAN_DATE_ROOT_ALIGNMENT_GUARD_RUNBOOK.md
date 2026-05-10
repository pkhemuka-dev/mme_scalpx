# Batch 30J-R5AQ Runbook

Purpose:
Prevent false-date materialization by checking that each R5AP materialization plan date aligns with group roots and usable source files.

Proof:
`run/proofs/proof_batch30j_r5aq_materialization_plan_date_root_alignment_guard_latest.json`

Classified plans:
`run/audits/batch30j_r5aq_materialization_plan_date_root_alignment_guard_20260510_105804/classified_plans.json`

Accepted candidates:
`run/audits/batch30j_r5aq_materialization_plan_date_root_alignment_guard_20260510_105804/accepted_candidates.json`

Date mismatch candidates:
`run/audits/batch30j_r5aq_materialization_plan_date_root_alignment_guard_20260510_105804/date_mismatch_candidates.json`

Invalid date candidates:
`run/audits/batch30j_r5aq_materialization_plan_date_root_alignment_guard_20260510_105804/invalid_date_candidates.json`

Next:
Inspect accepted candidates; staging-only materialization may proceed only if optional context gaps are accepted.
