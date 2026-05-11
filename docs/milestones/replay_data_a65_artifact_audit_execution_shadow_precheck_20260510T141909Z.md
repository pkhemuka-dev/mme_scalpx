# REPLAY-DATA-A65 artifact audit + execution-shadow scope precheck

{
  "a64_nested_run_dir": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
  "a66_preview_command_shell": ".venv/bin/python bin/replay_run.py --dataset-root run/replay/parity/offline_materialization --dataset-id session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z --selection-mode single_day --single-day 2026-04-17 --doctrine-mode locked --speed-mode accelerated --required-file-stems quote_ticks_mme_fut_stream,quote_ticks_mme_opt_stream --optional-file-stems features_rows_candidate,strategy_decisions_candidate,risk_outputs_candidate,execution_shadow_candidate,source_manifest,health_features --supported-suffixes .csv,.json,.jsonl --scope feeds_features_strategy_risk_execution_shadow --run-label a66_guarded_feeds_features_strategy_risk_execution_shadow_execution --run-root run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z",
  "a66_preview_generated": false,
  "a66_preview_path": "run/replay/a65_execution_shadow_scope_precheck/20260510T141909Z/feeds_features_strategy_risk_execution_shadow_PREVIEW_ONLY_NOT_EXECUTED.sh",
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
  "batch": "REPLAY-DATA-A65",
  "blocker_count": 1,
  "blockers": [
    "A64 integrity failure is not clearly limited to quote-only/economics metadata; execution-shadow precheck blocked"
  ],
  "broker_calls_executed": false,
  "candidate_count": 0,
  "classification": "FAIL_A65_GATE_BLOCKED_NO_EXECUTION_SHADOW_AUTHORIZATION",
  "command_executed": false,
  "economics_pnl_evaluation_allowed": false,
  "execution_shadow_execution_started": false,
  "execution_shadow_precheck_ok": false,
  "features_row_count": 165650,
  "full_engine_replay_allowed": false,
  "integrity_report": {
    "check_count": 6,
    "checks": [
      {
        "check_name": "heartbeat_integrity",
        "details": {
          "checked_files": [
            "execution_shadow_candidate.csv",
            "features_rows_candidate.csv",
            "health_features.json",
            "quote_ticks_mme_fut_stream.csv",
            "quote_ticks_mme_opt_stream.csv",
            "reconstruction_todo.json",
            "risk_outputs_candidate.csv",
            "source_manifest.json",
            "strategy_decisions_candidate.csv"
          ],
          "empty_file_count": 0,
          "file_count": 9,
          "missing_path_count": 0
        },
        "finished_at": "2026-05-10T14:04:12Z",
        "message": "heartbeat_integrity real check pass",
        "started_at": "2026-05-10T14:04:12Z",
        "verdict": "pass"
      },
      {
        "check_name": "hash_freshness",
        "details": {
          "file_count": 9,
          "missing_hash_count": 0,
          "missing_hash_files": []
        },
        "finished_at": "2026-05-10T14:04:12Z",
        "message": "hash_freshness real check pass",
        "started_at": "2026-05-10T14:04:12Z",
        "verdict": "pass"
      },
      {
        "check_name": "snapshot_sync_validity",
        "details": {
          "file_count": 9,
          "parseable_file_count": 9,
          "unsupported_suffix_files": []
        },
        "finished_at": "2026-05-10T14:04:12Z",
        "message": "snapshot_sync_validity real check pass",
        "started_at": "2026-05-10T14:04:12Z",
        "verdict": "pass"
      },
      {
        "check_name": "stale_leg_detection",
        "details": {
          "missing_stems": [
            "fut_ticks",
            "opt_ticks"
          ],
          "present_stems": [
            "execution_shadow_candidate",
            "features_rows_candidate",
            "health_features",
            "quote_ticks_mme_fut_stream",
            "quote_ticks_mme_opt_stream",
            "reconstruction_todo",
            "risk_outputs_candidate",
            "source_manifest",
            "strategy_decisions_candidate"
          ],
          "required_stems": [
            "fut_ticks",
            "opt_ticks"
          ]
        },
        "finished_at": "2026-05-10T14:04:12Z",
        "message": "stale_leg_detection real check failed",
        "started_at": "2026-05-10T14:04:12Z",
        "verdict": "fail"
      },
      {
        "check_name": "reset_cleanliness",
        "details": {
          "manifest_path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
          "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92"
        },
        "finished_at": "2026-05-10T14:04:12Z",
        "message": "reset_cleanliness real check pass",
        "started_at": "2026-05-10T14:04:12Z",
        "verdict": "pass"
      },
      {
        "check_name": "reproducibility_proof",
        "details": {
          "run_config_type": "ReplayRunConfig",
          "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
          "selection_fingerprint": "605c697db8399362febacbf0746588113ca4f1cc651139cd9007d2c5791a63fa"
        },
        "finished_at": "2026-05-10T14:04:12Z",
        "message": "reproducibility_proof real check pass",
        "started_at": "2026-05-10T14:04:12Z",
        "verdict": "pass"
      }
    ],
    "failed_checks": 1,
    "integrity_bundle": {
      "check_count": 6,
      "executed_checks": [
        {
          "check_name": "heartbeat_integrity",
          "details": {
            "checked_files": [
              "execution_shadow_candidate.csv",
              "features_rows_candidate.csv",
              "health_features.json",
              "quote_ticks_mme_fut_stream.csv",
              "quote_ticks_mme_opt_stream.csv",
              "reconstruction_todo.json",
              "risk_outputs_candidate.csv",
              "source_manifest.json",
              "strategy_decisions_candidate.csv"
            ],
            "empty_file_count": 0,
            "file_count": 9,
            "missing_path_count": 0
          },
          "finished_at": "2026-05-10T14:04:12Z",
          "message": "heartbeat_integrity real check pass",
          "started_at": "2026-05-10T14:04:12Z",
          "verdict": "pass"
        },
        {
          "check_name": "hash_freshness",
          "details": {
            "file_count": 9,
            "missing_hash_count": 0,
            "missing_hash_files": []
          },
          "finished_at": "2026-05-10T14:04:12Z",
          "message": "hash_freshness real check pass",
          "started_at": "2026-05-10T14:04:12Z",
          "verdict": "pass"
        },
        {
          "check_name": "snapshot_sync_validity",
          "details": {
            "file_count": 9,
            "parseable_file_count": 9,
            "unsupported_suffix_files": []
          },
          "finished_at": "2026-05-10T14:04:12Z",
          "message": "snapshot_sync_validity real check pass",
          "started_at": "2026-05-10T14:04:12Z",
          "verdict": "pass"
        },
        {
          "check_name": "stale_leg_detection",
          "details": {
            "missing_stems": [
              "fut_ticks",
              "opt_ticks"
            ],
            "present_stems": [
              "execution_shadow_candidate",
              "features_rows_candidate",
              "health_features",
              "quote_ticks_mme_fut_stream",
              "quote_ticks_mme_opt_stream",
              "reconstruction_todo",
              "risk_outputs_candidate",
              "source_manifest",
              "strategy_decisions_candidate"
            ],
            "required_stems": [
              "fut_ticks",
              "opt_ticks"
            ]
          },
          "finished_at": "2026-05-10T14:04:12Z",
          "message": "stale_leg_detection real check failed",
          "started_at": "2026-05-10T14:04:12Z",
          "verdict": "fail"
        },
        {
          "check_name": "reset_cleanliness",
          "details": {
            "manifest_path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
            "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92"
          },
          "finished_at": "2026-05-10T14:04:12Z",
          "message": "reset_cleanliness real check pass",
          "started_at": "2026-05-10T14:04:12Z",
          "verdict": "pass"
        },
        {
          "check_name": "reproducibility_proof",
          "details": {
            "run_config_type": "ReplayRunConfig",
            "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
            "selection_fingerprint": "605c697db8399362febacbf0746588113ca4f1cc651139cd9007d2c5791a63fa"
          },
          "finished_at": "2026-05-10T14:04:12Z",
          "message": "reproducibility_proof real check pass",
          "started_at": "2026-05-10T14:04:12Z",
          "verdict": "pass"
        }
      ],
      "failed_checks": 1,
      "notes": [],
      "passed_checks": 5,
      "required_checks": [
        "heartbeat_integrity",
        "hash_freshness",
        "snapshot_sync_validity",
        "stale_leg_detection",
        "reset_cleanliness",
        "reproducibility_proof"
      ],
      "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
      "verdict": "fail",
      "waivers": [],
      "warned_checks": 0
    },
    "notes": [],
    "passed_checks": 5,
    "verdict": "fail",
    "warned_checks": 0
  },
  "integrity_verdict": "fail",
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "metrics_summary": {
    "metrics": {
      "stage_count": 4
    },
    "notes": []
  },
  "new_replay_execution_started": false,
  "next_batch": "REPAIR_A65_BLOCKERS",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "risk_action_breakdown": {
    "HOLD": 165650
  },
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
  "run_summary_replay_scope": "feeds_features_strategy_risk",
  "run_summary_stage_names": [
    "feeds",
    "features",
    "strategy",
    "risk"
  ],
  "source_a64_r7": "run/proofs/proof_replay_data_a64_r7_topology_source_repair_audit_20260510T141618Z.json",
  "strategy_action_breakdown": {
    "HOLD": 165650
  },
  "strategy_row_count": 165650,
  "trade_count": 0,
  "verdict": "FAIL_A65_ARTIFACT_AUDIT_EXECUTION_SHADOW_PRECHECK",
  "warning_count": 1,
  "warnings": [
    "A64 integrity verdict is not pass: fail"
  ]
}
