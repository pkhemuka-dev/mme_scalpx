# LANE-B-R5E_COMPARE_BASELINE_SHADOW_PATCH_IMPACT_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_154016
2026-06-07T15:40:16+05:30

LAW=COMPARE_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

R5D_PROOF=run/proofs/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907.json
{
  "tag": "LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907",
  "classification": "PASS_R5D_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_EXECUTED_AND_SOURCE_RESTORED",
  "temporary_source_swap": true,
  "final_source_restore_required": true,
  "patch_applied": false,
  "replay_executed": true,
  "baseline_run_dir": "run/replay/lane_b_r5d/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907/baseline_pre_r27e_r27g/replay_locked_single_day_lane-b-r5d_execute_baseline_shadow_patch_impact_replay_no_patch_final_restore_no_order_20260607_143907_baseline_pre_r27e_r27g_20260607_090922_285d6f57",
  "shadow_run_dir": "run/replay/lane_b_r5d/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907/shadow_current/replay_locked_single_day_lane-b-r5d_execute_baseline_shadow_patch_impact_replay_no_patch_final_restore_no_order_20260607_143907_shadow_current_20260607_091411_07aa6771",
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "report": "run/audits/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907_report.md",
  "log": "run/logs/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907_execution.log"
}

{
  "all_compared_outputs_match": true,
  "baseline": {
    "blocker_distribution_sha256": "a23be5592b4da3ffb9a6c33d40b743544adca794c55607c6ddc01cd30c6a451d",
    "candidate_audit": {
      "actions": {
        "HOLD": 134035
      },
      "blockers": {
        "economics_fail": 134035
      },
      "candidates_true": 0,
      "columns": [
        "row_index",
        "event_time",
        "source_frame_id",
        "action",
        "candidate",
        "candidate_fallback",
        "selected_leg",
        "side",
        "linked_feature_side",
        "metadata_side",
        "blocker_name",
        "blocker_reason",
        "blocker_reason_fallback",
        "economics_reason",
        "reason"
      ],
      "exists": true,
      "rows": 134035,
      "sides": {
        "CALL": 56400,
        "CONTEXT": 21808,
        "PUT": 55827
      }
    },
    "run_dir": "run/replay/lane_b_r5d/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907/baseline_pre_r27e_r27g/replay_locked_single_day_lane-b-r5d_execute_baseline_shadow_patch_impact_replay_no_patch_final_restore_no_order_20260607_143907_baseline_pre_r27e_r27g_20260607_090922_285d6f57",
    "summary": {
      "candidate_count": 0,
      "execution_shadow_action_breakdown": {},
      "execution_shadow_filled_count": 0,
      "execution_shadow_row_count": 134035,
      "feature_leg_breakdown": {
        "CALL_ATM": 56400,
        "FUTURES": 21808,
        "PUT_ATM": 55827
      },
      "feature_row_count": 134035,
      "feature_side_breakdown": {
        "CALL": 56400,
        "CONTEXT": 21808,
        "PUT": 55827
      },
      "integrity_verdict": "pass",
      "pnl_total": null,
      "replay_scope": "feeds_features_strategy_risk_execution_shadow",
      "risk_action_breakdown": {
        "HOLD": 134035
      },
      "risk_row_count": 134035,
      "strategy_action_breakdown": {
        "HOLD": 134035
      },
      "strategy_row_count": 134035,
      "trade_count": 0
    }
  },
  "blocker_distribution_sha_match": true,
  "candidate_audit_checks": {
    "actions": true,
    "blockers": true,
    "candidates_true": true,
    "rows": true,
    "sides": true
  },
  "interpretation": "Pre-R27E/R27G baseline and current shadow produce identical no-candidate/no-fill outputs on A7 2026-06-02. Patch-impact on this dataset is zero at replay output level.",
  "pnl_result": "NO_TRADE_NO_PNL",
  "shadow": {
    "blocker_distribution_sha256": "a23be5592b4da3ffb9a6c33d40b743544adca794c55607c6ddc01cd30c6a451d",
    "candidate_audit": {
      "actions": {
        "HOLD": 134035
      },
      "blockers": {
        "economics_fail": 134035
      },
      "candidates_true": 0,
      "columns": [
        "row_index",
        "event_time",
        "source_frame_id",
        "action",
        "candidate",
        "candidate_fallback",
        "selected_leg",
        "side",
        "linked_feature_side",
        "metadata_side",
        "blocker_name",
        "blocker_reason",
        "blocker_reason_fallback",
        "economics_reason",
        "reason"
      ],
      "exists": true,
      "rows": 134035,
      "sides": {
        "CALL": 56400,
        "CONTEXT": 21808,
        "PUT": 55827
      }
    },
    "run_dir": "run/replay/lane_b_r5d/LANE-B-R5D_EXECUTE_BASELINE_SHADOW_PATCH_IMPACT_REPLAY_NO_PATCH_FINAL_RESTORE_NO_ORDER_20260607_143907/shadow_current/replay_locked_single_day_lane-b-r5d_execute_baseline_shadow_patch_impact_replay_no_patch_final_restore_no_order_20260607_143907_shadow_current_20260607_091411_07aa6771",
    "summary": {
      "candidate_count": 0,
      "execution_shadow_action_breakdown": {},
      "execution_shadow_filled_count": 0,
      "execution_shadow_row_count": 134035,
      "feature_leg_breakdown": {
        "CALL_ATM": 56400,
        "FUTURES": 21808,
        "PUT_ATM": 55827
      },
      "feature_row_count": 134035,
      "feature_side_breakdown": {
        "CALL": 56400,
        "CONTEXT": 21808,
        "PUT": 55827
      },
      "integrity_verdict": "pass",
      "pnl_total": null,
      "replay_scope": "feeds_features_strategy_risk_execution_shadow",
      "risk_action_breakdown": {
        "HOLD": 134035
      },
      "risk_row_count": 134035,
      "strategy_action_breakdown": {
        "HOLD": 134035
      },
      "strategy_row_count": 134035,
      "trade_count": 0
    }
  },
  "summary_checks": {
    "candidate_count": true,
    "execution_shadow_action_breakdown": true,
    "execution_shadow_filled_count": true,
    "execution_shadow_row_count": true,
    "feature_leg_breakdown": true,
    "feature_row_count": true,
    "feature_side_breakdown": true,
    "integrity_verdict": true,
    "pnl_total": true,
    "replay_scope": true,
    "risk_action_breakdown": true,
    "risk_row_count": true,
    "strategy_action_breakdown": true,
    "strategy_row_count": true,
    "trade_count": true
  }
}
COMPARE_RC=0

CLASSIFICATION=PASS_R5E_BASELINE_SHADOW_MATCH_NO_PATCH_IMPACT_NO_TRADE_NO_PNL
