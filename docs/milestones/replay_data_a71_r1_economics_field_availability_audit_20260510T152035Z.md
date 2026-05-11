# REPLAY-DATA-A71-R1 economics field availability audit only

{
  "actual_nested_run_dir": "run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e",
  "advisories": [
    "A71-R1 is audit-only and does not run economics/PnL.",
    "Zero candidates/trades/fills means economics/PnL remains blocked even if some price fields exist.",
    "Next valid lane action after A71-R1 is A72 candidate/trade/fill dataset discovery audit only."
  ],
  "availability": {
    "execution_shadow": {
      "field_counts": {
        "execution_action": {
          "present_count": 0,
          "truthy_count": 0
        },
        "fill_price": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "filled": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "order_action": {
          "present_count": 0,
          "truthy_count": 0
        },
        "pnl": {
          "present_count": 0,
          "truthy_count": 0
        },
        "realized_pnl": {
          "present_count": 0,
          "truthy_count": 0
        }
      },
      "row_count": 165650,
      "sample_keys": [
        "event_time",
        "execution_channel",
        "execution_id",
        "fill_price",
        "fill_qty",
        "filled",
        "metadata",
        "reason",
        "risk_action",
        "slippage",
        "source_risk_id",
        "symbol"
      ]
    },
    "features": {
      "field_counts": {
        "economics_valid": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "entry_price": {
          "present_count": 0,
          "truthy_count": 0
        },
        "exit_price": {
          "present_count": 0,
          "truthy_count": 0
        },
        "feature_economics_valid": {
          "present_count": 0,
          "truthy_count": 0
        },
        "feed_input_economics_evaluable": {
          "present_count": 0,
          "truthy_count": 0
        },
        "option_ltp": {
          "present_count": 0,
          "truthy_count": 0
        },
        "selected_option_ltp": {
          "present_count": 0,
          "truthy_count": 0
        },
        "spread": {
          "present_count": 165650,
          "truthy_count": 294
        },
        "spread_pct": {
          "present_count": 0,
          "truthy_count": 0
        }
      },
      "row_count": 165650,
      "sample_keys": [
        "ambiguity",
        "ambiguity_raw",
        "ask",
        "bid",
        "blocker",
        "candidate",
        "candidate_seed",
        "candidate_seed_raw",
        "cost_ticks",
        "economics_reason",
        "economics_valid",
        "economics_valid_raw",
        "entry_mode",
        "event_time",
        "feature_channel",
        "frame_id",
        "frame_ts",
        "fut_ltp",
        "futures_context",
        "healthy",
        "healthy_raw",
        "leg",
        "ltp",
        "metadata",
        "mid_price",
        "regime_ok",
        "regime_pass",
        "regime_pass_raw",
        "regime_reason",
        "replay_source_surface",
        "reward_cost_ratio",
        "reward_cost_valid",
        "reward_cost_valid_raw",
        "reward_ticks",
        "schema_version",
        "selected_leg",
        "side",
        "source_channel",
        "source_file",
        "source_frame_id",
        "source_sequence_id",
        "source_stem",
        "spread",
        "stop_ticks",
        "symbol",
        "target_ticks",
        "tick_size",
        "ts_event"
      ]
    },
    "risk": {
      "field_counts": {
        "economics_valid": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "entry_allowed": {
          "present_count": 0,
          "truthy_count": 0
        },
        "qty": {
          "present_count": 0,
          "truthy_count": 0
        },
        "risk_action": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "risk_economics_valid": {
          "present_count": 0,
          "truthy_count": 0
        },
        "risk_veto": {
          "present_count": 0,
          "truthy_count": 0
        }
      },
      "row_count": 165650,
      "sample_keys": [
        "allowed",
        "blocker_name",
        "blocker_name_fallback",
        "blocker_reason",
        "blocker_reason_fallback",
        "candidate",
        "candidate_fallback",
        "decision_id",
        "decision_id_fallback",
        "economics_valid",
        "economics_valid_fallback",
        "entry_mode",
        "event_time",
        "frame_id",
        "frame_id_fallback",
        "input_action",
        "linked_strategy_action",
        "linked_strategy_decision_id",
        "ltp",
        "metadata",
        "mid_price",
        "reason",
        "regime_pass",
        "regime_pass_fallback",
        "risk_action",
        "risk_channel",
        "risk_id",
        "risk_ts",
        "side",
        "side_fallback",
        "source_decision_id",
        "source_frame_id",
        "source_frame_id_fallback",
        "spread",
        "symbol",
        "veto_entry",
        "veto_reason",
        "vetoed"
      ]
    },
    "strategy": {
      "field_counts": {
        "candidate": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "candidate_found": {
          "present_count": 0,
          "truthy_count": 0
        },
        "economics_valid": {
          "present_count": 165650,
          "truthy_count": 0
        },
        "entry_price": {
          "present_count": 0,
          "truthy_count": 0
        },
        "stop_price": {
          "present_count": 0,
          "truthy_count": 0
        },
        "strategy_economics_valid": {
          "present_count": 0,
          "truthy_count": 0
        },
        "target_price": {
          "present_count": 0,
          "truthy_count": 0
        }
      },
      "row_count": 165650,
      "sample_keys": [
        "action",
        "blocker_name",
        "blocker_name_fallback",
        "blocker_reason",
        "blocker_reason_fallback",
        "candidate",
        "candidate_fallback",
        "decision_action",
        "decision_channel",
        "decision_id",
        "decision_ts",
        "decision_ts_fallback",
        "economics_reason",
        "economics_valid",
        "economics_valid_fallback",
        "entry_mode",
        "event_time",
        "frame_id",
        "frame_id_fallback",
        "linked_feature_frame_id",
        "linked_feature_leg",
        "linked_feature_side",
        "ltp",
        "metadata",
        "mid_price",
        "reason",
        "reason_chain",
        "regime_pass",
        "regime_pass_fallback",
        "reward_cost_ratio",
        "reward_ticks",
        "selected_leg",
        "selected_leg_fallback",
        "side",
        "side_fallback",
        "source_frame_id",
        "source_frame_id_fallback",
        "spread",
        "stop_ticks",
        "symbol",
        "target_ticks",
        "tick_size",
        "ts_event",
        "ts_event_fallback"
      ]
    }
  },
  "batch": "REPLAY-DATA-A71-R1",
  "blocker_count": 4,
  "blockers": [
    "economics field availability insufficient: economics valid/fill truth counts are zero or incomplete",
    "economics lifecycle unavailable: candidate_count is zero",
    "economics lifecycle unavailable: trade_count is zero",
    "economics lifecycle unavailable: execution_shadow_filled_count is zero"
  ],
  "broker_calls_executed": false,
  "candidate_count": 0,
  "classification": "ECONOMICS_FIELDS_NOT_READY_NO_EXECUTION",
  "command_executed": false,
  "economics_field_audit_only": true,
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "economics_valid_counts": {
    "execution_shadow_filled_true_count": 0,
    "feature_economics_valid_true_count": 0,
    "risk_economics_valid_true_count": 0,
    "strategy_economics_valid_true_count": 0
  },
  "execution_shadow_filled_count": 0,
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "REPLAY-DATA-A72 candidate/trade/fill dataset discovery audit only",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "source_a70_r1": "run/proofs/proof_replay_data_a70_r1_stem_alias_contract_patch_20260510T150529Z.json",
  "stem_alias_contract": "etc/replay/datasets/stem_alias_contract_v1.json",
  "trade_count": 0,
  "verdict": "PASS_A71_R1_ECONOMICS_FIELD_AUDIT_BLOCKED_AS_EXPECTED",
  "warning_count": 0,
  "warnings": []
}
