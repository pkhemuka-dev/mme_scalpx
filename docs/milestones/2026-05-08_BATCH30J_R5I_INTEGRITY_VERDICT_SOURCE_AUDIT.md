# Batch 30J-R5I — Integrity Verdict Source Audit

Verdict: `PASS_AUDIT_CLASSIFIED_SOURCE_REPAIR_REQUIRED`
Classification: `INTEGRITY_VERDICT_AGGREGATION_INVERSION_OR_DEFAULT_FAIL`

Integrity report:
`/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/guarded_offline/batch30j_r5f_20260417_20260508_123636/replay_locked_single_day_20260508_070637_863ee401/03_integrity_report.json`

Observed:
- top verdict: `fail`
- bundle verdict: `fail`
- failed_checks: `0`
- bundle failed_checks: `0`
- check_count: `12`
- derived_should_pass: `True`

No patch.
No replay execution.
No metadata mutation.
No Redis deletion.
No broker/order path.
No risk/execution start.

Next:
Write minimal patch batch for integrity verdict aggregation only, then rerun guarded replay.
