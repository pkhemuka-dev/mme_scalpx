# REPLAY-DATA-A73-R2 alternate fill-bearing dataset scan

{
  "advisories": [
    "A73-R2 is scan/admission-prep only. It does not run replay and does not authorize A74 execution.",
    "If a fill-ready dataset is found, the next batch must be A73-R3 strict admission gate for that exact dataset.",
    "Full-system/economics remain blocked until exact dataset admission and separate preview/gate pass."
  ],
  "alternate_fill_dataset_scan_only": true,
  "batch": "REPLAY-DATA-A73-R2",
  "blocker_count": 1,
  "blockers": [
    "no alternate execution-shadow CSV found with both nonzero filled_qty and nonzero fill_price plus required matching dataset files"
  ],
  "broker_calls_executed": false,
  "candidate_shadow_file_count": 4,
  "classification": "NO_ADMISSIBLE_FILL_DATASET_FOUND_FULL_SYSTEM_ECONOMICS_STILL_BLOCKED",
  "command_executed": false,
  "dataset_admitted": false,
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "fill_ready_count": 0,
  "fill_ready_sample": [],
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "STOP_NO_FILL_BEARING_DATASET_FOUND_OR_BUILD_PROPER_FILL_DATASET",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "partial_fill_count": 0,
  "partial_fill_sample": [],
  "searched_roots": [
    "run/replay/parity/offline_materialization",
    "run/replay/guarded_offline",
    "run/replay"
  ],
  "selected_candidate": null,
  "source_a73": "run/proofs/proof_replay_data_a73_dataset_admission_gate_20260510T152554Z.json",
  "unsafe_sample": [],
  "unsafe_shadow_file_count": 0,
  "verdict": "PASS_A73_R2_NO_FILL_BEARING_DATASET_ADMITTED",
  "warning_count": 0,
  "warnings": []
}
