# Batch 30J-R4L-R3 — Final Replay-Command Safety Gate Rerun

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: FINAL_REPLAY_COMMAND_SAFETY_GATE_RERUN_PASSED_WITH_ONE_DATE_REVIEW

Quiet seconds: 20

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Planned command: `.venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --selection-mode single_day --single-day 2026-04-29 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label lane_c_30j_r4j_planned_only_not_executed --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root`

Command scan: {
  "cmd_list": [
    ".venv/bin/python",
    "bin/replay_run.py",
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
  "cmd_string": ".venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --selection-mode single_day --single-day 2026-04-29 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label lane_c_30j_r4j_planned_only_not_executed --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root",
  "contains_shell_metacharacters": false,
  "contains_broker_order_live_terms": false,
  "has_required_args": true,
  "uses_shadow_execution_scope": true,
  "not_full_system_replay": true,
  "single_day": "2026-04-29",
  "dataset_id": "observe_only_replay_input_9c50b37fb4782fb0",
  "dataset_root": "run/replay/parity/offline_materialization",
  "run_root": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root"
}

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

Artifact files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/guarded_reversible_install_30j_r4k_20260507_151309/17_final_replay_command_safety_gate_rerun.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/guarded_reversible_install_30j_r4k_20260507_151309/18_30j_r5_readiness.json"
]

Blockers: []

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_ACCEPTED_FOR_CONTROLLED_REPLAY_ATTEMPT"
]

Next: Review one-date limitation, then run 30J-R5 guarded offline replay execution attempt with pre/post safety checks; no broker/order/live.

Safety: no replay execution, no metadata mutation, no Redis write/delete, no service start/stop, no paper/live, no orders.
