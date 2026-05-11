# REPLAY-DATA-A63-R4 false-positive repair risk scope gate

{
  "a62_source": "run/proofs/proof_replay_data_a62_strategy_artifact_risk_precheck_20260510T064052Z.json",
  "a64_direct": "run/replay/a63_r4_feeds_features_strategy_risk_gate/20260510T074544Z/A64_DIRECT_COMMAND_DO_NOT_RUN_UNTIL_LANE_C_CLEARED.sh",
  "a64_execution_performed": false,
  "a64_requires_lane_c_clearance": true,
  "a64_run_root": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_20260510T074544Z",
  "a64_runner": "run/replay/a63_r4_feeds_features_strategy_risk_gate/20260510T074544Z/A64_DURABLE_RUNNER_DO_NOT_RUN_UNTIL_LANE_C_CLEARED.sh",
  "a64_runner_generated": true,
  "batch": "REPLAY-DATA-A63-R4",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "PASS_GATE_ONLY_A64_GENERATED_NOT_EXECUTED_LANE_C_CLEARANCE_REQUIRED",
  "command_executed": false,
  "dataset_id": "session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z",
  "dataset_root": "run/replay/parity/offline_materialization",
  "day_dir": "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z/2026-04-17",
  "economics_pnl_evaluation_allowed": false,
  "engine_execution_performed": false,
  "full_engine_replay_allowed": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "next_batch": "REPLAY-DATA-A64 only after Lane C clearance",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "replay_run_executed": false,
  "services_started": false,
  "single_day": "2026-04-17",
  "strategy_action_breakdown": {
    "HOLD": 165650
  },
  "strategy_candidate_true_count": 0,
  "strategy_row_count": 165650,
  "verdict": "PASS",
  "warning_count": 1,
  "warnings": [
    "A64 execution requires Lane C dependency clearance before running because Lane C owns bin/replay_run.py guarded seam behavior."
  ]
}
