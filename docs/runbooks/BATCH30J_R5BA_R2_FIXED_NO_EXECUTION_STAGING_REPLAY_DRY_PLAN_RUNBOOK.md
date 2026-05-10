# Batch 30J-R5BA-R2 Runbook

Purpose:
Fixed no-execution validation of staging replay command shape and static fut requirement audit.

Proof:
`run/proofs/proof_batch30j_r5ba_r2_fixed_no_execution_staging_replay_dry_plan_latest.json`

Staging day detail:
`run/audits/batch30j_r5ba_r2_fixed_no_execution_staging_replay_dry_plan_20260510_120220/staging_day_detail.json`

Staging shapes:
`run/audits/batch30j_r5ba_r2_fixed_no_execution_staging_replay_dry_plan_20260510_120220/staging_shapes.json`

Fut requirement classification:
`run/audits/batch30j_r5ba_r2_fixed_no_execution_staging_replay_dry_plan_20260510_120220/fut_requirement_static_classification.json`

Code expectations:
`run/audits/batch30j_r5ba_r2_fixed_no_execution_staging_replay_dry_plan_20260510_120220/code_expectations.json`

Planned command:
`run/audits/batch30j_r5ba_r2_fixed_no_execution_staging_replay_dry_plan_20260510_120220/planned_command.txt`

Next:
Do not execute replay. Locate/materialize real fut_ticks.jsonl for 2026-04-18 or add a no-execution option-only compatibility proof.
