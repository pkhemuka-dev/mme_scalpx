# REPLAY-DATA-A68 full-system/economics readiness audit only

{
  "actual_nested_run_dir": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
  "advisories": [
    "A68 is readiness audit only. It must not generate/run full-system/economics commands.",
    "A67 execution-shadow chain remains valid and complete, but full-system/economics remain blocked."
  ],
  "artifact_files": {
    "10_run_summary.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/10_run_summary.json",
      "size_bytes": 2625
    },
    "engine_result.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/engine_result.json",
      "size_bytes": 5100
    },
    "execution_shadow_results.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/execution_shadow_results.json",
      "size_bytes": 128285663
    },
    "features_rows.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/features_rows.json",
      "size_bytes": 936126710
    },
    "risk_outputs.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/risk_outputs.json",
      "size_bytes": 292603094
    },
    "strategy_decisions.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/strategy_decisions.json",
      "size_bytes": 328097971
    }
  },
  "batch": "REPLAY-DATA-A68",
  "blocker_count": 8,
  "blockers": [
    "full-system/economics readiness blocked: integrity_verdict is fail; prior stale-leg stem-equivalence waiver is acceptable for execution-shadow audit only, not for full-system/economics promotion",
    "economics/readiness blocked: ml_export_eligible is False",
    "economics readiness blocked: feature_economics_valid_true_count is zero/null",
    "economics readiness blocked: strategy_economics_valid_true_count is zero/null",
    "economics readiness blocked: risk_economics_valid_true_count is zero/null",
    "full-system readiness blocked: candidate_count is zero; no entry lifecycle exercised",
    "full-system/economics readiness blocked: trade_count is zero",
    "full-system/economics readiness blocked: execution_shadow_filled_count is zero"
  ],
  "broker_calls_executed": false,
  "candidate_count": 0,
  "classification": "BLOCKED_FULL_SYSTEM_ECONOMICS_NOT_READY_NO_EXECUTION",
  "command_executed": false,
  "economics_fields": {
    "execution_shadow_filled_count": 0,
    "feature_economics_valid_true_count": 0,
    "pnl_total": null,
    "risk_economics_valid_true_count": 0,
    "strategy_economics_valid_true_count": 0,
    "trade_count": 0
  },
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "engine_result_summary": {
    "engine_finished_at": "2026-05-10T14:25:16Z",
    "engine_started_at": "2026-05-10T14:24:22Z",
    "final_state": "completed",
    "notes": [],
    "run_id": "replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
    "stage_count": 5,
    "stage_records": [
      {
        "finished_at": "2026-05-10T14:24:34Z",
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
          "run_id": "replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
          "stage_name": "feeds",
          "status": "ok",
          "total_injected": 165650
        },
        "stage_name": "feeds",
        "started_at": "2026-05-10T14:24:22Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:25:09Z",
        "order_index": 1,
        "output_summary": {
          "feature_channel": "replay:features",
          "feature_frames_published": 165650,
          "mode": "replay_feature_bridge",
          "run_id": "replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
          "source_feed_events": 165650,
          "stage_name": "features",
          "status": "ok"
        },
        "stage_name": "features",
        "started_at": "2026-05-10T14:24:34Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:25:11Z",
        "order_index": 2,
        "output_summary": {
          "action_breakdown": {
            "HOLD": 165650
          },
          "decision_channel": "replay:decisions",
          "mode": "replay_strategy_bridge",
          "run_id": "replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
          "source_feature_frames": 165650,
          "stage_name": "strategy",
          "status": "ok",
          "strategy_decisions_published": 165650
        },
        "stage_name": "strategy",
        "started_at": "2026-05-10T14:25:09Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:25:12Z",
        "order_index": 3,
        "output_summary": {
          "mode": "replay_risk_bridge",
          "risk_action_breakdown": {
            "HOLD": 165650
          },
          "risk_channel": "replay:risk",
          "risk_outputs_published": 165650,
          "run_id": "replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
          "source_strategy_decisions": 165650,
          "stage_name": "risk",
          "status": "ok",
          "vetoed_entries": 0
        },
        "stage_name": "risk",
        "started_at": "2026-05-10T14:25:11Z",
        "success": true,
        "terminal_stage": false
      },
      {
        "finished_at": "2026-05-10T14:25:16Z",
        "order_index": 4,
        "output_summary": {
          "execution_channel": "replay:execution_shadow",
          "execution_results_published": 165650,
          "fill_model_name": "immediate_market",
          "filled_count": 0,
          "mode": "replay_execution_shadow_bridge",
          "run_id": "replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
          "source_risk_outputs": 165650,
          "stage_name": "execution_shadow",
          "status": "ok"
        },
        "stage_name": "execution_shadow",
        "started_at": "2026-05-10T14:25:12Z",
        "success": true,
        "terminal_stage": true
      }
    ],
    "topology_summary": {
      "notes": [],
      "scope": "feeds_features_strategy_risk_execution_shadow",
      "stage_names": [
        "feeds",
        "features",
        "strategy",
        "risk",
        "execution_shadow"
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
          "terminal_stage": false
        },
        {
          "description": "Replay-only execution shadow stage with no live side effects.",
          "order_index": 4,
          "owns_runtime_decisioning": true,
          "stage_name": "execution_shadow",
          "terminal_stage": true
        }
      ],
      "topology_fingerprint": "4b6fc95a56eb8cd691208a5c21bd70994aa136956bd1f683863f0090813eda59"
    }
  },
  "execution_shadow_action_breakdown": {},
  "execution_shadow_filled_count": 0,
  "execution_shadow_row_count": 165650,
  "features_row_count": 165650,
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "integrity_verdict": "fail",
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "metrics_summary": {
    "metrics": {
      "stage_count": 5
    },
    "notes": []
  },
  "ml_export_eligible": false,
  "new_replay_execution_started": false,
  "next_batch": "STOP_FULL_SYSTEM_ECONOMICS_BLOCKED_REPAIR_DATASET_INTEGRITY_AND_ECONOMICS_FIRST",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "readiness_audit_only": true,
  "risk_action_breakdown": {
    "HOLD": 165650
  },
  "risk_row_count": 165650,
  "root_artifacts": {
    "00_manifest.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/00_manifest.json",
      "size_bytes": 5278
    },
    "01_dataset_summary.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/01_dataset_summary.json",
      "size_bytes": 9659
    },
    "02_scope_profile.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/02_scope_profile.json",
      "size_bytes": 18043
    },
    "03_integrity_report.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/03_integrity_report.json",
      "size_bytes": 7561
    },
    "04_metrics_summary.json": {
      "exists": true,
      "path": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/04_metrics_summary.json",
      "size_bytes": 59
    }
  },
  "run_summary_replay_scope": "feeds_features_strategy_risk_execution_shadow",
  "run_summary_stage_count": 5,
  "run_summary_stage_names": [
    "feeds",
    "features",
    "strategy",
    "risk",
    "execution_shadow"
  ],
  "source_a67": "run/proofs/proof_replay_data_a67_post_execution_shadow_audit_next_scope_precheck_20260510T142850Z.json",
  "strategy_action_breakdown": {
    "HOLD": 165650
  },
  "strategy_row_count": 165650,
  "trade_count": 0,
  "verdict": "PASS_A68_READINESS_AUDIT_BLOCKED_AS_EXPECTED",
  "warning_count": 0,
  "warnings": []
}
