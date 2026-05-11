# REPLAY-DATA-A63-R5 Lane C clearance review + A64 refresh gate only

{
  "a62_source": {
    "ok": true,
    "path": "run/proofs/proof_replay_data_a62_strategy_artifact_risk_precheck_20260510T064052Z.json"
  },
  "a63_r4_source": {
    "ok": true,
    "path": "run/proofs/proof_replay_data_a63_r4_feeds_features_strategy_risk_gate_20260510T074544Z.json"
  },
  "a64_direct": "run/replay/a63_r5_lane_c_clearance_review_a64_gate/20260510T133906Z/A64_DIRECT_COMMAND_LANE_C_CLEARED_DO_NOT_RUN_AUTOMATICALLY.sh",
  "a64_execution_performed": false,
  "a64_run_root": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_lane_c_clearance_20260510T133906Z",
  "a64_runner": "run/replay/a63_r5_lane_c_clearance_review_a64_gate/20260510T133906Z/A64_DURABLE_RUNNER_LANE_C_CLEARED_DO_NOT_RUN_AUTOMATICALLY.sh",
  "a64_runner_refreshed": false,
  "batch": "REPLAY-DATA-A63-R5",
  "blocker_count": 5,
  "blockers": [
    "R5BE-R4B did not apply patch",
    "R5BE-R4B target_sha_after missing",
    "R5BF lane_c_clearance_ready not true",
    "R5BF unexpectedly authorized A64 execution",
    "current bin/replay_run.py sha does not match R5BF target_sha256"
  ],
  "broker_calls_executed": false,
  "classification": "FAIL_LANE_C_CLEARANCE_REVIEW_BLOCKED_A64_NOT_AUTHORIZED",
  "command_executed": false,
  "current_replay_run_sha256": "d6e073c8af006e1a4e6d7dc11c84fd7dc00f14497dab32ae2270d5d74a6edc6d",
  "economics_pnl_evaluation_allowed": false,
  "engine_execution_performed": false,
  "full_engine_replay_allowed": false,
  "lane_c_r5be_source": {
    "ok": true,
    "path": "run/proofs/proof_batch30j_r5be_r4b_exact_scoped_guarded_patch_latest.json"
  },
  "lane_c_r5bf_source": {
    "ok": true,
    "path": "run/proofs/proof_batch30j_r5bf_no_execution_cli_guard_validation_latest.json"
  },
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "next_batch": "REPAIR_A63_R5_BLOCKERS",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "r5bf_target_sha256": null,
  "replay_run_executed": false,
  "services_started": false,
  "verdict": "FAIL",
  "warning_count": 0,
  "warnings": []
}
