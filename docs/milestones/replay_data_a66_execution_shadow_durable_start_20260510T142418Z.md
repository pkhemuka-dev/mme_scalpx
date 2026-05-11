# REPLAY-DATA-A66 execution-shadow durable start

{
  "a65_r2_source": "run/proofs/proof_replay_data_a65_r2_integrity_stem_equivalence_execution_shadow_precheck_20260510T142256Z.json",
  "a66_command_shell": ".venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z --selection-mode single_day --single-day 2026-04-17 --doctrine-mode locked --speed-mode accelerated --required-file-stems quote_ticks_mme_fut_stream,quote_ticks_mme_opt_stream --optional-file-stems features_rows_candidate,strategy_decisions_candidate,risk_outputs_candidate,execution_shadow_candidate,source_manifest,health_features --supported-suffixes .csv,.json,.jsonl --scope feeds_features_strategy_risk_execution_shadow --run-label a66_guarded_execution_shadow_after_a65_r2 --run-root run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z",
  "batch": "REPLAY-DATA-A66-START",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "direct": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/A66_DIRECT_EXECUTION_SHADOW_COMMAND.sh",
  "economics_pnl_evaluation_allowed": false,
  "execution_shadow_durable_started": true,
  "full_engine_replay_allowed": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "log": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/logs/a66_replay_run.log",
  "next_batch": "REPLAY-DATA-A66 completion monitor / artifact audit after process exits",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "pid_file": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/logs/a66_replay_run.pid",
  "run_root": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z",
  "runner": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/A66_DURABLE_EXECUTION_SHADOW_RUNNER.sh",
  "runner_start_returncode": 0,
  "runner_stderr": "",
  "runner_stdout": "===== REPLAY-DATA-A66 DURABLE EXECUTION-SHADOW START =====\n2026-05-10T19:54:18+05:30\npid=258702\nlog=run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/logs/a66_replay_run.log\nrun_root=run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z\n",
  "verdict": "PASS_A66_EXECUTION_SHADOW_DURABLE_STARTED"
}
