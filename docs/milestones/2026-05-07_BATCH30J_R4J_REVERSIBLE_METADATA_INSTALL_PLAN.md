# Batch 30J-R4J — Reversible Metadata Install Plan + Dry CLI Validation

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: REVERSIBLE_INSTALL_PLAN_READY_WITH_ONE_DATE_REVIEW

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Planned CLI: `.venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --selection-mode single_day --single-day 2026-04-29 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label lane_c_30j_r4j_planned_only_not_executed --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root`

Dry argparse validation: {
  "args": [
    "--dataset-root",
    "run/replay/parity/offline_materialization",
    "--dataset-id",
    "observe_only_replay_input_9c50b37fb4782fb0",
    "--selection-mode",
    "single_day",
    "--single-day",
    "2026-04-29",
    "--doctrine-mode",
    "locked",
    "--scope",
    "feeds_features_strategy_risk_execution_shadow",
    "--speed-mode",
    "accelerated",
    "--run-label",
    "lane_c_30j_r4j_planned_only_not_executed",
    "--run-root",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root"
  ],
  "ok": true,
  "namespace": {
    "dataset_root": "run/replay/parity/offline_materialization",
    "selection_mode": "single_day",
    "single_day": "2026-04-29",
    "start_date": null,
    "end_date": null,
    "custom_dates": null,
    "weekdays": null,
    "months": null,
    "window_start": null,
    "window_end": null,
    "session_segment": null,
    "doctrine_mode": "locked",
    "scope": "feeds_features_strategy_risk_execution_shadow",
    "speed_mode": "accelerated",
    "run_label": "lane_c_30j_r4j_planned_only_not_executed",
    "experiment_profile": null,
    "override_pack_id": null,
    "dataset_id": "observe_only_replay_input_9c50b37fb4782fb0",
    "fill_model": null,
    "run_root": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root",
    "required_file_stems": null,
    "optional_file_stems": null,
    "supported_suffixes": null,
    "recurse": false,
    "clock_start_time": null,
    "channel_prefix": null
  },
  "single_day_valid": true,
  "dataset_root_exists": true,
  "dataset_id_present": true,
  "run_root_present": true,
  "scope_is_shadow": true,
  "not_full_system_replay": true
}

Install plan status: PLAN_ONLY_NOT_INSTALLED

Artifact files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/11_reversible_metadata_install_plan_and_dry_cli_validation.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/12_30j_r4k_readiness.json"
]

Blockers: []

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_ACCEPTED_FOR_CONTROLLED_NEXT_STEP"
]

Next: Review one-date limitation, then run 30J-R4K guarded reversible metadata install + immediate dry CLI selector validation only; no replay execution.

Safety: plan only; no metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
