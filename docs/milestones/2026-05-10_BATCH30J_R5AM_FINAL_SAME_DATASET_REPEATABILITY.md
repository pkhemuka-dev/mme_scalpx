# Batch 30J-R5AM — Final Same-Dataset Replay Repeatability After Fingerprint Patch

Verdict: `PASS_SINGLE_DATE_REPLAY_REPRODUCIBILITY_FINAL`
Classification: `SAME_DATASET_ID_A_B_REPLAY_REPEATABLE_AFTER_FINGERPRINT_PATCH`

Selected date:
`2026-04-17`

Dataset ID:
`repository_confirmed_repeatability_probe_same_id`

Run A:
`run/replay/guarded_offline/batch30j_r5am_final_repeatability_20260417_20260510_103932_run_a/replay_locked_single_day_20260510_050932_5d964b2c`

Run B:
`run/replay/guarded_offline/batch30j_r5am_final_repeatability_20260417_20260510_103932_run_b/replay_locked_single_day_20260510_050933_f4523b26`

Runtime clean after:
`True`

Runs clean:
`True`

Selection fingerprint equal:
`True`

Effective input fingerprint equal:
`True`

Stage outputs equal:
`True`

Control equal after timestamp drop:
`True`

No paper/live enablement.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution service start.

Next:
Proceed to offline historic date ingestion/selection plan to add more repository-confirmed dates for all-strategy offline testing.
