# Batch 30J-R3 — Required Replay CLI Args Repair

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: REQUIRED_REPLAY_CLI_ARGS_REPAIR_BLOCKED

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Inferred single day: None

Repair dir: None

Files changed: []

Repaired command:

```json
null
```

Blockers: [
  "SINGLE_DAY_INFERRED_BLOCKER"
]

Review: [
  "REPAIR_DIR_CREATED_REVIEW",
  "REPAIR_FILES_WRITTEN_REVIEW",
  "REPAIRED_COMMAND_HAS_REQUIRED_FLAGS_REVIEW"
]

Next: Do not run replay. Resolve 30J-R3 blockers first.

Safety: artifact-only command repair; no replay execution, no materialization, no Redis write/delete, no service start/stop, no paper/live, no orders.
