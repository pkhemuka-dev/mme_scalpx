# Batch 30I — Guarded Replay Dry-Run Command Construction

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: DRY_RUN_COMMAND_CONSTRUCTED_WITH_REVIEW_ITEMS

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Selected entrypoint: bin/replay_run.py

Command dir: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_construction_30i

Files changed: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_construction_30i/00_guarded_replay_dry_run_command_contract.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_dry_run_command_construction_30i/01_30j_readiness_contract.json"
]

Constructed command:

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
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0"
  ],
  "constructed_command_shell": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py --dataset-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0",
  "entrypoint": "bin/replay_run.py",
  "executed_in_30i": false,
  "notes": [
    "NO_CONFIRMED_DRY_RUN_FLAG_IN_ENTRYPOINT_AST",
    "NO_CONFIRMED_OUTPUT_FLAG_IN_ENTRYPOINT_AST"
  ],
  "safe_to_promote_to_execution_in_later_batch": false
}
```

Blockers: []

Review: ["CONSTRUCTED_COMMAND_REQUIRES_CLI_FLAG_REVIEW_BEFORE_30J", "CONSTRUCTED_COMMAND_SAFE_TO_PROMOTE_LATER_REVIEW"]

Next: Batch 30I-R2 — inspect/repair command contract warnings; no replay execution.

Safety: artifact-only command construction; no replay execution, no materialization, no Redis write/delete, no service start/stop, no paper/live, no orders.
