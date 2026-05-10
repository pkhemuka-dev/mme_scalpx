# Batch 30J-R5BA-R2 — Fixed No-Execution Staging Replay Dry-Plan / Fut Requirement Audit

Verdict: `REVIEW_FUT_TICKS_HARD_REQUIRED_BEFORE_REPLAY`
Classification: `MISSING_FUT_TICKS_BLOCKS_STAGING_REPLAY_EXECUTION`

Raw date:
`2026-04-18`

Final dates:
[
  "2026-04-17"
]

Staging dates:
[
  "2026-04-18"
]

Final repository untouched:
`True`

Staging repository load OK:
`True`

Fut requirement classification:
`FUT_TICKS_APPEARS_HARD_REQUIRED_BY_STATIC_CODE`

Replay command was not executed:
`.venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/r5ay_raw_to_replay --dataset-id staging_only_20260418_probe --selection-mode single_day --single-day 2026-04-18 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --run-root run/replay/guarded_offline/batch30j_r5bb_staging_execution_probe_20260418_20260510_120220`

R2 fix:
Previous R5BA failed because `PYBIN` was undefined inside Python. R2 uses `PYBIN_CMD`.

No replay execution.
No final repository mutation.
No new staging materialization.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Do not execute replay. Locate/materialize real fut_ticks.jsonl for 2026-04-18 or add a no-execution option-only compatibility proof.
