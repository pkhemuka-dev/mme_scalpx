# Batch 30J-R2 — Guarded Offline Replay Dry-Run Execution Retry

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: GUARDED_OFFLINE_REPLAY_DRY_RUN_RETRY_FAILED_OR_SAFETY_DRIFT

Previous 30J parser issue: nested 30I-R3 broker/order path field was not read correctly.

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Run root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root

Command:

```bash
/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root --run-label batch30j_guarded_offline_replay_dry_run
```

Execution rc: 2

Blockers: [
  "REPLAY_COMMAND_NONZERO_OR_TIMEOUT_BLOCKER",
  "REPLAY_OUTPUT_NOT_CREATED_BLOCKER"
]

Review: [
  "PRIOR_30I_R3_LITERAL_OR_COMMENT_ONLY_BROKER_TEXT_ACCEPTED_FOR_30J_R2"
]

Run root inspection:

```json
{
  "candidate_like": [],
  "csv_count": 0,
  "decision_like": [],
  "exists": true,
  "file_count": 0,
  "is_dir": true,
  "json_count": 0,
  "json_inspection": [],
  "log_count": 0,
  "manifest_like": [],
  "parquet_count": 0,
  "path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root",
  "summary_like": [],
  "total_bytes": 0,
  "trade_like": [],
  "tree_top": []
}
```

Next: Do not continue parity. Diagnose 30J-R2 blockers first.

Safety: no broker/order/live, no service starts, no Redis key deletion, no paper/live enablement. This is offline replay execution only.
