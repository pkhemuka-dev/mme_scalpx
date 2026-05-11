# REPLAY-DATA-A63-R7 Lane C R5BH handoff inspection + A64 refresh gate only

{
  "a62_source": {
    "ok": true,
    "path": "run/proofs/proof_replay_data_a62_strategy_artifact_risk_precheck_20260510T064052Z.json"
  },
  "a63_r4_source": {
    "ok": true,
    "path": "run/proofs/proof_replay_data_a63_r4_feeds_features_strategy_risk_gate_20260510T074544Z.json"
  },
  "a64_direct": "run/replay/a63_r7_lane_c_r5bh_handoff_a64_gate/20260510T134335Z/A64_DIRECT_COMMAND_LANE_C_HANDOFF_CLEARED_DO_NOT_RUN_AUTOMATICALLY.sh",
  "a64_execution_performed": false,
  "a64_run_root": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bh_handoff_20260510T134335Z",
  "a64_runner": "run/replay/a63_r7_lane_c_r5bh_handoff_a64_gate/20260510T134335Z/A64_DURABLE_RUNNER_LANE_C_HANDOFF_CLEARED_DO_NOT_RUN_AUTOMATICALLY.sh",
  "a64_runner_refreshed": false,
  "batch": "REPLAY-DATA-A63-R7",
  "blocker_count": 2,
  "blockers": [
    "R5BH lane_c_done not true",
    "R5BH unexpectedly authorized A64 execution"
  ],
  "broker_calls_executed": false,
  "classification": "FAIL_LANE_C_HANDOFF_REVIEW_BLOCKED_A64_NOT_AUTHORIZED",
  "clearance_bundle": "run/evidence_bundles/lane_c_clearance_r5bf_20260510_190302.tar.gz",
  "clearance_bundle_sha": "run/evidence_bundles/lane_c_clearance_r5bf_20260510_190302.tar.gz.sha256",
  "clearance_pointer": "run/evidence_bundles/LATEST_LANE_C_CLEARANCE_BUNDLE.txt",
  "command_executed": false,
  "current_replay_run_sha256": "d6e073c8af006e1a4e6d7dc11c84fd7dc00f14497dab32ae2270d5d74a6edc6d",
  "economics_pnl_evaluation_allowed": false,
  "engine_execution_performed": false,
  "full_engine_replay_allowed": false,
  "handoff_note": "run/handoffs/LANE_C_TO_LANE_E_R5BF_CLEARANCE_HANDOFF.txt",
  "lane_c_r5bh_source": {
    "ok": true,
    "path": "run/proofs/proof_batch30j_r5bh_r1_corrected_handoff_verifier_latest.json"
  },
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "next_batch": "REPAIR_A63_R7_BLOCKERS",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "r5bh_expected_sha256": null,
  "replay_run_executed": false,
  "services_started": false,
  "verdict": "FAIL",
  "warning_count": 1,
  "warnings": [
    "R5BH expected replay_run sha not found; current sha recorded but not compared."
  ]
}
