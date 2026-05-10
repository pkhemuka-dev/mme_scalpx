# Batch 30J-R5AX Runbook

Purpose:
Design a staging-only raw-to-replay mapping contract for `2026-04-18`, based on R5AW proof that raw ticks can feed the existing derived replay pipeline.

Proof:
`run/proofs/proof_batch30j_r5ax_staging_only_raw_to_replay_contract_design_latest.json`

Contract:
`run/audits/batch30j_r5ax_staging_only_raw_to_replay_contract_design_20260510_114819/staging_contract.json`

Raw shapes:
`run/audits/batch30j_r5ax_staging_only_raw_to_replay_contract_design_20260510_114819/raw_shapes.json`

Known repository ABI reference:
`run/audits/batch30j_r5ax_staging_only_raw_to_replay_contract_design_20260510_114819/known_day_detail.json`

Source scans:
`run/audits/batch30j_r5ax_staging_only_raw_to_replay_contract_design_20260510_114819/source_scans.json`

Next:
Run R5AY staging-only dry materialization for 2026-04-18; write only under run/replay/staging, no run/replay final mutation and no replay execution.
