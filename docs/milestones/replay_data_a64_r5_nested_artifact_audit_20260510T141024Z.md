# REPLAY-DATA-A64-R5 nested run-dir artifact audit repair only

{
  "actual_nested_run_dir": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
  "artifact_audit_only": true,
  "artifact_files": {
    "10_run_summary.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/10_run_summary.json",
      "size_bytes": 2624
    },
    "engine_result.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/engine_result.json",
      "size_bytes": 4337
    },
    "features_rows.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/features_rows.json",
      "size_bytes": 943580960
    },
    "risk_outputs.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/risk_outputs.json",
      "size_bytes": 292603094
    },
    "strategy_decisions.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/strategy_decisions.json",
      "size_bytes": 328097971
    }
  },
  "batch": "REPLAY-DATA-A64-R5",
  "blocker_count": 2,
  "blockers": [
    "engine topology scope is not feeds_features_strategy_risk",
    "engine topology stages not feeds/features/strategy/risk"
  ],
  "broker_calls_executed": false,
  "candidate_dirs": [
    {
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
      "score": 5
    }
  ],
  "classification": "FAIL_A64_NESTED_ARTIFACT_AUDIT_BLOCKED",
  "command_executed": false,
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
  "features_row_count": 165650,
  "full_engine_replay_allowed": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "log": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.log",
  "log_tail": [
    "          {",
    "            \"line_count\": 8126,",
    "            \"modified_at_utc\": \"2026-05-08T19:41:33Z\",",
    "            \"name\": \"quote_ticks_mme_fut_stream.csv\",",
    "            \"relative_path\": \"quote_ticks_mme_fut_stream.csv\",",
    "            \"row_count\": 8125,",
    "            \"sha256\": \"58b27e8518e22220189a9fbd27bc0680a2444e3dca6cff73b8afa98bd83bea65\",",
    "            \"size_bytes\": 1770628,",
    "            \"stem\": \"quote_ticks_mme_fut_stream\",",
    "            \"suffix\": \".csv\"",
    "          },",
    "          {",
    "            \"line_count\": 25006,",
    "            \"modified_at_utc\": \"2026-05-08T19:41:33Z\",",
    "            \"name\": \"quote_ticks_mme_opt_stream.csv\",",
    "            \"relative_path\": \"quote_ticks_mme_opt_stream.csv\",",
    "            \"row_count\": 25005,",
    "            \"sha256\": \"c34ff0859176c8c7249ecc5a6b92b3fb0b7587a9748965afc6ccd6d1f42378ed\",",
    "            \"size_bytes\": 5217596,",
    "            \"stem\": \"quote_ticks_mme_opt_stream\",",
    "            \"suffix\": \".csv\"",
    "          },",
    "          {",
    "            \"line_count\": 13,",
    "            \"modified_at_utc\": \"2026-05-08T17:37:39Z\",",
    "            \"name\": \"reconstruction_todo.json\",",
    "            \"relative_path\": \"reconstruction_todo.json\",",
    "            \"row_count\": null,",
    "            \"sha256\": \"15589a278a75cb6f526c3b1807a299b5afffe18a843071238ceb34022456fc53\",",
    "            \"size_bytes\": 809,",
    "            \"stem\": \"reconstruction_todo\",",
    "            \"suffix\": \".json\"",
    "          },",
    "          {",
    "            \"line_count\": 33131,",
    "            \"modified_at_utc\": \"2026-05-08T19:41:37Z\",",
    "            \"name\": \"risk_outputs_candidate.csv\",",
    "            \"relative_path\": \"risk_outputs_candidate.csv\",",
    "            \"row_count\": 33130,",
    "            \"sha256\": \"385554bb40d59ef63e569eeb7a72ba908b7eb90d0705ca4c8a77e16d7463c074\",",
    "            \"size_bytes\": 10635614,",
    "            \"stem\": \"risk_outputs_candidate\",",
    "            \"suffix\": \".csv\"",
    "          },",
    "          {",
    "            \"line_count\": 353,",
    "            \"modified_at_utc\": \"2026-05-08T17:37:39Z\",",
    "            \"name\": \"source_manifest.json\",",
    "            \"relative_path\": \"source_manifest.json\",",
    "            \"row_count\": null,",
    "            \"sha256\": \"a08985898d699651ec040c035bf83fa9aa3365a56423e21b5daa3889deee8b89\",",
    "            \"size_bytes\": 12327,",
    "            \"stem\": \"source_manifest\",",
    "            \"suffix\": \".json\"",
    "          },",
    "          {",
    "            \"line_count\": 33131,",
    "            \"modified_at_utc\": \"2026-05-08T19:41:36Z\",",
    "            \"name\": \"strategy_decisions_candidate.csv\",",
    "            \"relative_path\": \"strategy_decisions_candidate.csv\",",
    "            \"row_count\": 33130,",
    "            \"sha256\": \"5a9b8650cced23334ffedac6800fff3cadae215e3aa608426c3f7863d460f0f7\",",
    "            \"size_bytes\": 12240377,",
    "            \"stem\": \"strategy_decisions_candidate\",",
    "            \"suffix\": \".csv\"",
    "          }",
    "        ]",
    "      }",
    "    ],",
    "    \"selection_fingerprint\": \"605c697db8399362febacbf0746588113ca4f1cc651139cd9007d2c5791a63fa\",",
    "    \"selection_mode\": \"single_day\",",
    "    \"selection_notes\": [],",
    "    \"session_segment\": null,",
    "    \"trading_dates\": [",
    "      \"2026-04-17\"",
    "    ]",
    "  },",
    "  \"status\": \"ok\",",
    "  \"topology_plan\": {",
    "    \"notes\": [],",
    "    \"scope\": \"feeds_features_strategy_risk\",",
    "    \"stage_names\": [",
    "      \"feeds\",",
    "      \"features\",",
    "      \"strategy\",",
    "      \"risk\"",
    "    ],",
    "    \"stages\": [",
    "      {",
    "        \"description\": \"Replay input publication / feed-stage chain entry.\",",
    "        \"order_index\": 0,",
    "        \"owns_runtime_decisioning\": false,",
    "        \"stage_name\": \"feeds\",",
    "        \"terminal_stage\": false",
    "      },",
    "      {",
    "        \"description\": \"Feature computation stage driven from replayed feed truth.\",",
    "        \"order_index\": 1,",
    "        \"owns_runtime_decisioning\": true,",
    "        \"stage_name\": \"features\",",
    "        \"terminal_stage\": false",
    "      },",
    "      {",
    "        \"description\": \"Strategy decision stage driven from replay feature truth.\",",
    "        \"order_index\": 2,",
    "        \"owns_runtime_decisioning\": true,",
    "        \"stage_name\": \"strategy\",",
    "        \"terminal_stage\": false",
    "      },",
    "      {",
    "        \"description\": \"Risk gating stage applied to replay strategy outputs.\",",
    "        \"order_index\": 3,",
    "        \"owns_runtime_decisioning\": true,",
    "        \"stage_name\": \"risk\",",
    "        \"terminal_stage\": true",
    "      }",
    "    ],",
    "    \"topology_fingerprint\": \"78b1c5ad0596441f9a622eb30f8b763a9623ffdfb85446634cd00de1ee65f4bc\"",
    "  }",
    "}"
  ],
  "metrics_summary": {
    "metrics": {
      "stage_count": 4
    },
    "notes": []
  },
  "new_replay_execution_started": false,
  "next_batch": "REPAIR_A64_R5_BLOCKERS",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "pid": 257546,
  "ps_output": "",
  "risk_row_count": 165650,
  "root_artifacts": {
    "00_manifest.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
      "size_bytes": 5982
    },
    "01_dataset_summary.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/01_dataset_summary.json",
      "size_bytes": 9659
    },
    "02_scope_profile.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/02_scope_profile.json",
      "size_bytes": 17753
    },
    "03_integrity_report.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/03_integrity_report.json",
      "size_bytes": 7890
    },
    "04_metrics_summary.json": {
      "exists": true,
      "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/04_metrics_summary.json",
      "size_bytes": 59
    }
  },
  "run_summary": {
    "batch_profile": null,
    "blocker_count": 165650,
    "candidate_count": 0,
    "chapter": "replay",
    "completed_at": "2026-05-10T14:04:12Z",
    "created_at": "2026-05-10T14:03:12Z",
    "dataset_fingerprint": "332dae5b5a709fc0f9160690e2b94acb42799a0643344c47ab2f2f4f3ed08e39",
    "dataset_id": "session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z",
    "dataset_profile": null,
    "doctrine_mode": "locked",
    "duration_ms": null,
    "execution_shadow_action_breakdown": {},
    "execution_shadow_filled_count": 0,
    "execution_shadow_row_count": 0,
    "experiment_profile": null,
    "feature_blocker_non_null_count": 165650,
    "feature_candidate_true_count": 0,
    "feature_economics_valid_true_count": 0,
    "feature_leg_breakdown": {
      "CALL_ATM": 62555,
      "FUTURES": 40625,
      "PUT_ATM": 62470
    },
    "feature_regime_pass_true_count": 66260,
    "feature_row_count": 165650,
    "feature_side_breakdown": {
      "CALL": 25022,
      "CONTEXT": 16250,
      "PUT": 24988,
      "quote_ticks_mme_fut_stream": 24375,
      "quote_ticks_mme_opt_stream": 75015
    },
    "forensic_profile": null,
    "input_fingerprint": "605c697db8399362febacbf0746588113ca4f1cc651139cd9007d2c5791a63fa",
    "integrity_profile": null,
    "integrity_verdict": "fail",
    "loss_count": 0,
    "ml_export_eligible": false,
    "notes": [],
    "operator_verdict": null,
    "override_pack_id": null,
    "pnl_total": null,
    "regime_pass_count": 66260,
    "remarks": null,
    "replay_profile": null,
    "replay_scope": "feeds_features_strategy_risk",
    "research_tags": [],
    "risk_action_breakdown": {
      "HOLD": 165650
    },
    "risk_blocker_non_null_count": 165650,
    "risk_economics_valid_true_count": 0,
    "risk_regime_pass_true_count": 66260,
    "risk_row_count": 165650,
    "risk_vetoed_true_count": 0,
    "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
    "selection_mode": "single_day",
    "shadow_label": null,
    "side_mode": "mirrored_both",
    "speed_mode": "accelerated",
    "stage_count": 4,
    "stage_names": [
      "feeds",
      "features",
      "strategy",
      "risk"
    ],
    "started_at": "2026-05-10T14:03:12Z",
    "strategy_action_breakdown": {
      "HOLD": 165650
    },
    "strategy_blocker_non_null_count": 165650,
    "strategy_candidate_true_count": 0,
    "strategy_economics_valid_true_count": 0,
    "strategy_regime_pass_true_count": 66260,
    "strategy_row_count": 165650,
    "trade_count": 0,
    "trading_dates": [
      "2026-04-17"
    ],
    "waiver_count": 0,
    "win_count": 0,
    "window_end": null,
    "window_start": null
  },
  "source_a64_r3": "run/proofs/proof_replay_data_a64_r3_completion_monitor_20260510T140703Z.json",
  "strategy_row_count": 165650,
  "verdict": "FAIL_A64_NESTED_ARTIFACT_AUDIT",
  "warning_count": 0,
  "warnings": [],
  "wrapper_run_root": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z"
}
