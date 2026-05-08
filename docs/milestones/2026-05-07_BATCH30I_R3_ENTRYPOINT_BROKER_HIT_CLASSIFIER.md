# Batch 30I-R3 — Entrypoint Broker/Order Hit Classifier + Command Contract Repair

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: ENTRYPOINT_BROKER_HITS_CLASSIFIED_COMMAND_READY_WITH_NONCRITICAL_REVIEW

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Repair dir: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3

Files changed: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/00_repaired_replay_dry_run_command_contract.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/01_30j_guarded_execution_readiness.json"
]

Repaired command:

```json
{
  "confirmed_flags": [
    "--channel-prefix",
    "--clock-start-time",
    "--custom-dates",
    "--dataset-id",
    "--dataset-root",
    "--doctrine-mode",
    "--end-date",
    "--experiment-profile",
    "--fill-model",
    "--months",
    "--optional-file-stems",
    "--override-pack-id",
    "--recurse",
    "--required-file-stems",
    "--run-label",
    "--run-root",
    "--scope",
    "--selection-mode",
    "--session-segment",
    "--single-day",
    "--speed-mode",
    "--start-date",
    "--supported-suffixes",
    "--weekdays",
    "--window-end",
    "--window-start"
  ],
  "constructed_command": [
    "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python",
    "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py",
    "--dataset-root",
    "run/replay/parity/offline_materialization",
    "--dataset-id",
    "observe_only_replay_input_9c50b37fb4782fb0",
    "--run-root",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root",
    "--run-label",
    "batch30j_guarded_offline_replay_dry_run"
  ],
  "constructed_command_shell": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_repair_30i_r3/planned_30j_run_root --run-label batch30j_guarded_offline_replay_dry_run",
  "dataset_contract": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/refined_dataset_candidate_contract_30g_r2/00_refined_dataset_candidate_contract.json",
  "dataset_leaf": "observe_only_replay_input_9c50b37fb4782fb0",
  "dataset_parent": "run/replay/parity/offline_materialization",
  "dry_run_resolution": "NO_EXPLICIT_DRY_RUN_FLAG_REPLAY_RUN_IS_OFFLINE_REPLAY_ENTRYPOINT",
  "entrypoint": "bin/replay_run.py",
  "executed_in_30i_r3": false,
  "notes": [],
  "resolutions": [
    "DATASET_SELECTION_CONFIRMED_BY_DATASET_ROOT_AND_DATASET_ID",
    "OUTPUT_SINK_CONFIRMED_BY_RUN_ROOT",
    "RUN_LABEL_CONFIRMED_FOR_AUDITABILITY",
    "NO_EXPLICIT_DRY_RUN_FLAG_REPLAY_RUN_IS_OFFLINE_REPLAY_ENTRYPOINT"
  ],
  "safe_to_promote_to_30j_guarded_offline_execution": true
}
```

Entrypoint broker/order classification:

```json
{
  "dangerous_attrs": [],
  "dangerous_calls": [],
  "dangerous_imports": [],
  "direct_broker_order_path": false,
  "literal_or_comment_only_broker_order_hits": true
}
```

Blockers: []

Review: ["ENTRYPOINT_BROKER_ORDER_HITS_ARE_LITERAL_OR_COMMENT_ONLY"]

Next: Review non-critical warnings, then run Batch 30J if acceptable.

Safety: artifact-only repair; no replay execution, no materialization, no Redis write/delete, no service start/stop, no paper/live, no orders.
