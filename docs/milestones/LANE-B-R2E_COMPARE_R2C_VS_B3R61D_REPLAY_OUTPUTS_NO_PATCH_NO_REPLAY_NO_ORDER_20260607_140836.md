# LANE-B-R2E_COMPARE_R2C_VS_B3R61D_REPLAY_OUTPUTS_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_140836
2026-06-07T14:08:36+05:30

LAW=COMPARE_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

NEW_RUN_DIR=run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b
OLD_RUN_DIR=run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7

{
  "all_match": false,
  "checks": {
    "blocker_count": true,
    "blocker_distribution_sha256": true,
    "candidate_audit_actions": true,
    "candidate_audit_blocker_pairs": true,
    "candidate_audit_candidate_true_count": true,
    "candidate_audit_rows": true,
    "candidate_audit_side_counts": true,
    "candidate_count": true,
    "dataset_fingerprint": false,
    "feature_row_count": true,
    "input_fingerprint": false,
    "integrity_verdict": true,
    "strategy_action_breakdown": true,
    "strategy_row_count": true,
    "trade_count": true
  },
  "new": {
    "blocker_distribution_sha256": "a23be5592b4da3ffb9a6c33d40b743544adca794c55607c6ddc01cd30c6a451d",
    "candidate_audit": {
      "actions": {
        "HOLD": 134035
      },
      "blocker_pairs": {
        "economics_fail|no_entry_condition|no_entry_condition|CALL|CALL_ATM": 56400,
        "economics_fail|no_entry_condition|no_entry_condition|CONTEXT|FUTURES": 21808,
        "economics_fail|no_entry_condition|no_entry_condition|PUT|PUT_ATM": 55827
      },
      "candidate_true_count": 0,
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
      "side_counts": {
        "CALL": 56400,
        "CONTEXT": 21808,
        "PUT": 55827
      }
    },
    "run_summary": {
      "blocker_count": 134035,
      "candidate_count": 0,
      "dataset_fingerprint": "e0b34ae189c9dd5ad105656df39bafa844386ed75370c4b45cd27471a77b71c6",
      "dataset_id": "B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
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
      "input_fingerprint": "8639cc6da9a861e893ad5a80bbeb73ec9c7fc78231a806192fa4d05920ef051f",
      "integrity_verdict": "pass",
      "run_id": "replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
      "strategy_action_breakdown": {
        "HOLD": 134035
      },
      "strategy_row_count": 134035,
      "trade_count": 0
    }
  },
  "new_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
  "old": {
    "blocker_distribution_sha256": "a23be5592b4da3ffb9a6c33d40b743544adca794c55607c6ddc01cd30c6a451d",
    "candidate_audit": {
      "actions": {
        "HOLD": 134035
      },
      "blocker_pairs": {
        "economics_fail|no_entry_condition|no_entry_condition|CALL|CALL_ATM": 56400,
        "economics_fail|no_entry_condition|no_entry_condition|CONTEXT|FUTURES": 21808,
        "economics_fail|no_entry_condition|no_entry_condition|PUT|PUT_ATM": 55827
      },
      "candidate_true_count": 0,
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
      "side_counts": {
        "CALL": 56400,
        "CONTEXT": 21808,
        "PUT": 55827
      }
    },
    "run_summary": {
      "blocker_count": 134035,
      "candidate_count": 0,
      "dataset_fingerprint": "146146ec2700eaa772ee57a3fea700db3f2c865e014de6dbb87c981e377d856c",
      "dataset_id": "B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
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
      "input_fingerprint": "6e8c5748b935e4f9094c1219d5ef81f4dc020b357df5dd0a3e4085b53595cd8d",
      "integrity_verdict": "pass",
      "run_id": "replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7",
      "strategy_action_breakdown": {
        "HOLD": 134035
      },
      "strategy_row_count": 134035,
      "trade_count": 0
    }
  },
  "old_dir": "run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7"
}
COMPARE_RC=0

CLASSIFICATION=REVIEW_R2E_R2C_DIFFERS_FROM_FROZEN_B3R61D_INSPECT_DIFFS
