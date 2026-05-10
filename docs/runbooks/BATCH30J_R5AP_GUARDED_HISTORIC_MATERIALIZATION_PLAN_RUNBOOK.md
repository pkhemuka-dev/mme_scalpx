# Batch 30J-R5AP Runbook

Purpose:
Build a guarded materialization plan from R5AO, while rejecting proof/audit/contract/doc noise before any repository mutation.

Proof:
`run/proofs/proof_batch30j_r5ap_guarded_historic_materialization_plan_latest.json`

Materialization plans:
`run/audits/batch30j_r5ap_guarded_historic_materialization_plan_20260510_105626/materialization_plans.json`

Strong materializable plans:
`run/audits/batch30j_r5ap_guarded_historic_materialization_plan_20260510_105626/strong_materializable_plans.json`

Best plan summary:
`run/audits/batch30j_r5ap_guarded_historic_materialization_plan_20260510_105626/best_plan_by_date_summary.json`

Next:
Review materialization_plan; either run staging-only materialization for best candidate or inspect optional gaps.
