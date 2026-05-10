# Batch 30J-R5AJ — Same-Dataset-ID Replay Repeatability Final

Verdict: `REVIEW_SAME_DATASET_SELECTION_FINGERPRINT_STILL_DRIFTS`
Classification: `SELECTION_FINGERPRINT_DRIFT_NOT_ONLY_DATASET_ID`

Selected date:
`2026-04-17`

Dataset ID:
`repository_confirmed_repeatability_probe_same_id`

Run A:
`run/replay/guarded_offline/batch30j_r5aj_same_dataset_repeatability_20260417_20260510_101415_run_a/replay_locked_single_day_20260510_044415_11a896df`

Run B:
`run/replay/guarded_offline/batch30j_r5aj_same_dataset_repeatability_20260417_20260510_101415_run_b/replay_locked_single_day_20260510_044416_8cb40cb8`

Runtime clean after:
`True`

Runs clean:
`True`

Selection fingerprint equal:
`False`

Stage outputs equal:
`True`

Semantic equal:
`False`

No paper/live enablement.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution service start.

Next:
Inspect scope_profile/effective_inputs diffs and patch selection fingerprint contract if proven.
