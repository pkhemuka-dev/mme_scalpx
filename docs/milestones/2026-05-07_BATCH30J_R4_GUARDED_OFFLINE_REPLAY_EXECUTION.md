# Batch 30J-R4 — Guarded Offline Replay Execution

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: GUARDED_OFFLINE_REPLAY_R4_FAILED_OR_SAFETY_DRIFT

Dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Single day: 2026-05-03

Scope: feeds_features_strategy_risk_execution_shadow

Run root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/non_self_date_source_required_args_repair_30j_r3b/planned_30j_r4_run_root

Command:

```bash
/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --selection-mode single_day --single-day 2026-05-03 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/non_self_date_source_required_args_repair_30j_r3b/planned_30j_r4_run_root --run-label batch30j_r4_guarded_offline_replay_non_self_date_repair
```

Execution rc: 1

Output file count: 0

Blockers: [
  "REPLAY_COMMAND_NONZERO_OR_TIMEOUT_BLOCKER",
  "REPLAY_OUTPUT_NOT_CREATED_BLOCKER"
]

Review: []

Next: Do not continue parity. Diagnose 30J-R4 blockers first.

Safety: no broker/order/live, no service starts, no Redis key deletion, no paper/live enablement. This is offline replay execution only.
