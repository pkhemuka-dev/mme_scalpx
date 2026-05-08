# Batch 30I-R2 — Replay Command Contract Repair

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: REPLAY_COMMAND_CONTRACT_REPAIR_BLOCKED

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Repair dir: None

Files changed: []

Repaired command:

```json
null
```

Blockers: ["ENTRYPOINT_NO_DIRECT_BROKER_ORDER_HITS_BLOCKER"]

Review: ["REPAIRED_COMMAND_WRITTEN_REVIEW", "REPAIRED_COMMAND_SAFE_FOR_30J_REVIEW", "OUTPUT_WARNING_RESOLVED_REVIEW", "DRY_RUN_WARNING_RESOLVED_OR_EXPLAINED_REVIEW"]

Next: Do not run 30J. Resolve 30I-R2 blockers first.

Safety: artifact-only repair; no replay execution, no materialization, no Redis write/delete, no service start/stop, no paper/live, no orders.
