# Batch 30J-R5AT Runbook

Purpose:
Apply strict proof-noise and row-level date filters to R5AS candidates before any staging/materialization.

Proof:
`run/proofs/proof_batch30j_r5at_strict_row_level_source_group_planner_latest.json`

Strict source groups:
`run/audits/batch30j_r5at_strict_row_level_source_group_planner_20260510_113503/strict_source_groups.json`

Date summary:
`run/audits/batch30j_r5at_strict_row_level_source_group_planner_20260510_113503/date_summary.json`

Strict accepted files:
`run/audits/batch30j_r5at_strict_row_level_source_group_planner_20260510_113503/strict_accepted_files.json`

Rejected sample:
`run/audits/batch30j_r5at_strict_row_level_source_group_planner_20260510_113503/rejected_files_sample.json`

R5AS strong files reclassified:
`run/audits/batch30j_r5at_strict_row_level_source_group_planner_20260510_113503/r5as_strong_files_reclassified.json`

Next:
Do not materialize. Upload/locate raw captured source files with explicit source_date/trading_date or epoch event timestamps.
