# 30J-R5BR Runbook

Purpose: validate the R5BQ-R3 stem-equivalence repair without replay execution.

Validated fixture families:

- canonical opt_ticks/fut_ticks
- quote-stream aliases
- option-only alias still missing futures unless the separate guarded option-only seam is used
- unknown stems do not satisfy opt/fut
- ambiguous stems fail closed

Proof: `run/proofs/proof_batch30j_r5br_no_execution_stem_equivalence_fixture_validation_latest.json`
Validation report: `run/audits/batch30j_r5br_no_execution_stem_equivalence_fixture_validation_20260510_210224/r5br_fixture_validation_report.json`

Next, only if PASS: Lane E integrity gate. Do not jump straight to full-system/economics/PnL.
