# Batch 30J-R5AG — Single-Date Replay Repeatability / Reproducibility

Verdict: `REVIEW_REPEATABILITY_SEMANTIC_HASH_MISMATCH`
Classification: `REPLAY_REPEATABILITY_NOT_PROVEN_SEMANTIC_DIFF`

Selected date:
`2026-04-17`

Run A:
`run/replay/guarded_offline/batch30j_r5ag_repeatability_20260417_20260510_100312_run_a/replay_locked_single_day_20260510_043312_d749744e`

Run B:
`run/replay/guarded_offline/batch30j_r5ag_repeatability_20260417_20260510_100312_run_b/replay_locked_single_day_20260510_043312_97fd32da`

Runtime clean after:
`True`

Runs clean:
`True`

Semantic equal:
`False`

No paper/live enablement.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution service start.

Next:
Inspect stable_comparison mismatches and normalize or repair nondeterministic fields.
