# Batch 30H — Replay Dry-Run Plan + Adapter Compatibility Audit

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: REPLAY_DRY_RUN_PLAN_WRITTEN_WITH_REVIEW_ITEMS

Dataset path: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Dry-run plan dir: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_dry_run_plan_adapter_audit_30h

Files changed: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_dry_run_plan_adapter_audit_30h/00_replay_dry_run_adapter_compatibility_audit.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_dry_run_plan_adapter_audit_30h/01_guarded_replay_dry_run_plan.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_dry_run_plan_adapter_audit_30h/02_next_guarded_replay_dry_run_preflight_contract.json"
]

Adapter checks: {
  "bin_replay_entrypoint_present": true,
  "compile_ok": true,
  "contract_files_present": true,
  "contracts_surface_present": true,
  "dataset_has_load_or_select_surface": false,
  "dataset_surface_present": true,
  "engine_has_execute_or_run_surface": true,
  "engine_surface_present": true,
  "runner_has_run_or_main_surface": false,
  "runner_surface_present": true,
  "selected_dataset_path_present": true
}

Blockers: []

Review: ["RUNNER_RUN_MAIN_SURFACE_NOT_CONFIRMED_BY_AST", "DATASET_LOAD_SELECT_SURFACE_NOT_CONFIRMED_BY_AST"]

Next: Review 30H adapter warnings, then run Batch 30I if acceptable.

Safety: artifact-only plan/audit; no replay execution, no materialization, no Redis write/delete, no service start/stop, no paper/live, no orders.
