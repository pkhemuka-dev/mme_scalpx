# REPLAY-DATA-A64-R1 completion monitor + artifact audit only

{
  "a64_start_source": "run/proofs/proof_replay_data_a64_durable_execution_start_20260510T140306Z.json",
  "batch": "REPLAY-DATA-A64-R1",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "RUNNING_WAIT_AND_RERUN_A64_R1",
  "command_executed": false,
  "completion_monitor_only": true,
  "economics_pnl_evaluation_allowed": false,
  "engine_result": {
    "engine_finished_at": "2026-05-10T14:04:12Z",
    "engine_started_at": "2026-05-10T14:03:12Z",
    "final_state": "completed",
    "notes": [],
    "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
    "stage_count": 4,
    "stage_records": [
      {
        "finished_at": "2026-05-10T14:03:26Z",
        "order_index": 0,
        "output_summary": {
          "clock_after_stage": "2026-04-17T10:58:49Z",
          "day_breakdown": [
            {
              "injected_count": 165650,
              "last_sequence_id": 165650,
              "trading_day": "2026-04-17"
            }
          ],
          "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
          "stage_name": "feeds",
          "status": "ok",
          "total_injected": 165650
        },
        "stage_name": "feeds",
        "started_at": "2026-05-10T14:03:12Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:04:07Z",
        "order_index": 1,
        "output_summary": {
          "feature_channel": "replay:features",
          "feature_frames_published": 165650,
          "mode": "replay_feature_bridge",
          "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
          "source_feed_events": 165650,
          "stage_name": "features",
          "status": "ok"
        },
        "stage_name": "features",
        "started_at": "2026-05-10T14:03:26Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:04:10Z",
        "order_index": 2,
        "output_summary": {
          "action_breakdown": {
            "HOLD": 165650
          },
          "decision_channel": "replay:decisions",
          "mode": "replay_strategy_bridge",
          "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
          "source_feature_frames": 165650,
          "stage_name": "strategy",
          "status": "ok",
          "strategy_decisions_published": 165650
        },
        "stage_name": "strategy",
        "started_at": "2026-05-10T14:04:07Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:04:12Z",
        "order_index": 3,
        "output_summary": {
          "mode": "replay_risk_bridge",
          "risk_action_breakdown": {
            "HOLD": 165650
          },
          "risk_channel": "replay:risk",
          "risk_outputs_published": 165650,
          "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
          "source_strategy_decisions": 165650,
          "stage_name": "risk",
          "status": "ok",
          "vetoed_entries": 0
        },
        "stage_name": "risk",
        "started_at": "2026-05-10T14:04:10Z",
        "success": true,
        "terminal_stage": true
      }
    ],
    "topology_summary": {
      "notes": [],
      "scope": "feeds_features_strategy_risk",
      "stage_names": [
        "feeds",
        "features",
        "strategy",
        "risk"
      ],
      "stages": [
        {
          "description": "Replay input publication / feed-stage chain entry.",
          "order_index": 0,
          "owns_runtime_decisioning": false,
          "stage_name": "feeds",
          "terminal_stage": false
        },
        {
          "description": "Feature computation stage driven from replayed feed truth.",
          "order_index": 1,
          "owns_runtime_decisioning": true,
          "stage_name": "features",
          "terminal_stage": false
        },
        {
          "description": "Strategy decision stage driven from replay feature truth.",
          "order_index": 2,
          "owns_runtime_decisioning": true,
          "stage_name": "strategy",
          "terminal_stage": false
        },
        {
          "description": "Risk gating stage applied to replay strategy outputs.",
          "order_index": 3,
          "owns_runtime_decisioning": true,
          "stage_name": "risk",
          "terminal_stage": true
        }
      ],
      "topology_fingerprint": "78b1c5ad0596441f9a622eb30f8b763a9623ffdfb85446634cd00de1ee65f4bc"
    }
  },
  "engine_result_paths": [
    "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/engine_result.json"
  ],
  "file_count": 10,
  "files_sample": [
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.log",
      "size_bytes": 97
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.pid",
      "size_bytes": 7
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
      "size_bytes": 5982
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/01_dataset_summary.json",
      "size_bytes": 9659
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/02_scope_profile.json",
      "size_bytes": 17753
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/03_integrity_report.json",
      "size_bytes": 55
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/04_metrics_summary.json",
      "size_bytes": 59
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/17_effective_inputs.json",
      "size_bytes": 2406
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/18_effective_overrides_flat.json",
      "size_bytes": 347
    },
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/engine_result.json",
      "size_bytes": 4337
    }
  ],
  "full_engine_replay_allowed": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "log": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.log",
  "log_tail": [
    "===== REPLAY-DATA-A64 DIRECT AFTER R5BI SHAPE-TOLERANT CLEARANCE =====",
    "2026-05-10T19:33:06+05:30"
  ],
  "metrics_summary": {},
  "new_replay_execution_started": false,
  "next_batch": "RERUN_A64_R1_AFTER_PROCESS_EXITS",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "pid": 257546,
  "pid_file": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.pid",
  "process_alive": true,
  "rc_file": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.rc",
  "rc_value": null,
  "required_artifacts": {
    "00_manifest.json": {
      "exists": false,
      "size_bytes": null
    },
    "01_dataset_summary.json": {
      "exists": false,
      "size_bytes": null
    },
    "02_scope_profile.json": {
      "exists": false,
      "size_bytes": null
    },
    "03_integrity_report.json": {
      "exists": false,
      "size_bytes": null
    },
    "04_metrics_summary.json": {
      "exists": false,
      "size_bytes": null
    }
  },
  "risk_related_paths": [
    "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92"
  ],
  "run_root": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z",
  "run_summary_paths": [],
  "runner": "run/replay/a63_r11_r5bi_shape_tolerant_a64_gate/20260510T140201Z/A64_DURABLE_RUNNER_R5BI_SHAPE_TOLERANT_CLEARED_DO_NOT_RUN_AUTOMATICALLY.sh",
  "strategy_related_paths": [
    "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92"
  ],
  "verdict": "RUNNING_A64_PROCESS_STILL_ACTIVE_NOT_AUDITED",
  "warning_count": 1,
  "warnings": [
    "A64 runner did not capture rc file; completion verdict uses process status + artifacts/logs."
  ]
}
