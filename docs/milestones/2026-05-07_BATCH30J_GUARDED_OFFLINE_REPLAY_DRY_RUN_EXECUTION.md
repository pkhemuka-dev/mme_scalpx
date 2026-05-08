# Batch 30J — Guarded Offline Replay Dry-Run Execution

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: GUARDED_OFFLINE_REPLAY_DRY_RUN_FAILED_OR_SAFETY_DRIFT

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Run root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root

Command:

```bash
/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root --run-label batch30j_guarded_offline_replay_dry_run
```

Execution rc: None

Blockers: [
  "PRIOR_30I_R3_DIRECT_BROKER_ORDER_PATH_FALSE_BLOCKER"
]

Review: [
  "PRIOR_30I_R3_NONCRITICAL_REVIEW_ACCEPTED_FOR_30J"
]

Run root inspection:

```json
{
  "candidate_like": [],
  "csv_count": 0,
  "decision_like": [],
  "exists": false,
  "file_count": 0,
  "is_dir": false,
  "json_count": 0,
  "json_inspection": [],
  "log_count": 0,
  "manifest_like": [],
  "parquet_count": 0,
  "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root",
  "summary_like": [],
  "total_bytes": 0,
  "trade_like": [],
  "tree_top": []
}
```

Next: Do not continue parity. Diagnose 30J blockers first.

Safety: no broker/order/live, no service starts, no Redis key deletion, no paper/live enablement. This is offline replay execution only.
