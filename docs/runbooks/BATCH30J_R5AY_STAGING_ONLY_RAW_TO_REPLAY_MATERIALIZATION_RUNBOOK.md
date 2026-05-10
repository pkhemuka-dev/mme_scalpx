# Batch 30J-R5AY Runbook

Purpose:
Materialize raw `2026-04-18` rows into staging-only replay day input shape.

Proof:
`run/proofs/proof_batch30j_r5ay_staging_only_raw_to_replay_materialization_latest.json`

Staging day:
`run/replay/staging/r5ay_raw_to_replay/2026-04-18`

Source reports:
`run/audits/batch30j_r5ay_staging_only_raw_to_replay_materialization_20260510_115558/source_reports.json`

Split report:
`run/audits/batch30j_r5ay_staging_only_raw_to_replay_materialization_20260510_115558/split_report.json`

Staging day detail:
`run/audits/batch30j_r5ay_staging_only_raw_to_replay_materialization_20260510_115558/staging_day_detail.json`

Next:
Run R5AZ staging repository ABI/detail probe and no-execution replay command planning; no final run/replay mutation.
