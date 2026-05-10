# Batch 30J-R5AZ — Staging Repository ABI Probe / No-Execution Replay Plan

Verdict: `REVIEW_STAGING_ABI_LOADS_BUT_FUT_TICKS_MISSING_DOCUMENTED`
Classification: `STAGING_REPOSITORY_LOAD_OK_OPTION_ONLY_REPLAY_EXECUTION_RISK`

Raw date:
`2026-04-18`

Final replay dates:
[
  "2026-04-17"
]

Staging replay dates:
[
  "2026-04-18"
]

Final repo untouched:
`True`

Staging repository load OK:
`True`

Staging has option ticks:
`True`

Staging has futures ticks:
`False`

Futures missing documented:
`True`

Planned command was not executed:
`.venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/r5ay_raw_to_replay --dataset-id staging_only_20260418_probe --selection-mode single_day --single-day 2026-04-18 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --run-root run/replay/guarded_offline/batch30j_r5ba_staging_probe_20260418_20260510_115734`

No replay execution.
No final repository mutation.
No new staging materialization.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Run R5BA no-execution replay dry-plan/argument validation and inspect whether replay_run requires fut_ticks at execution; do not execute replay yet.
