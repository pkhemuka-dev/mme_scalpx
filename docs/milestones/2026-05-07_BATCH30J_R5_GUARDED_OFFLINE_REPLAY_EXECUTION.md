# Batch 30J-R5 — Guarded Offline Replay Execution Attempt

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: GUARDED_OFFLINE_REPLAY_EXECUTION_FAILED_OR_SAFETY_DRIFT

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Command: `.venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id observe_only_replay_input_9c50b37fb4782fb0 --selection-mode single_day --single-day 2026-04-29 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label lane_c_30j_r4j_planned_only_not_executed --run-root run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root`

Execution ok: False rc=1 timeout=False

Run root before: {
  "path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root",
  "exists": false,
  "file_count": 0,
  "json_count": 0,
  "csv_count": 0,
  "manifest_like": [],
  "summary_like": [],
  "first_files": []
}

Run root after: {
  "path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/planned_30j_r5_run_root",
  "exists": false,
  "file_count": 0,
  "json_count": 0,
  "csv_count": 0,
  "manifest_like": [],
  "summary_like": [],
  "first_files": []
}

Blockers: []

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_ACCEPTED_FOR_CONTROLLED_REPLAY_ATTEMPT",
  "REPLAY_EXECUTION_NONZERO_REVIEW"
]

Next: Do not continue parity. Diagnose 30J-R5 execution/runtime blockers first.

Safety: guarded offline replay only; no service start, no Redis key deletion, no paper/live, no broker order path, orders must remain zero.
