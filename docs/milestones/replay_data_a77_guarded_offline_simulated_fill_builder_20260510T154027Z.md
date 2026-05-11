# REPLAY-DATA-A77 guarded offline simulated-fill dataset builder only

{
  "advisories": [
    "A77 built an offline simulated-fill dataset only; it did not run replay/economics/backtest.",
    "Simulated fills are mechanics probes and are not real broker fills or strategy-profit proof.",
    "Next valid batch is A78 strict admission gate for the A77 output dataset only."
  ],
  "batch": "REPLAY-DATA-A77",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "SIMULATED_FILL_DATASET_BUILT_READY_FOR_A78_ADMISSION_GATE_FULL_SYSTEM_ECONOMICS_STILL_BLOCKED",
  "command_executed": false,
  "contract_path": "etc/replay/datasets/fill_bearing_dataset_build_contract_v1.json",
  "dataset_admitted_for_backtest": false,
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "fill_dataset_built": true,
  "fill_price_nonzero_count": 25005,
  "filled_qty_nonzero_count": 25005,
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "futures_row_count": 8125,
  "input_day_dir": "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z_cleaned_selected_day_a29_20260508T194132Z/2026-04-17",
  "input_execution_shadow_row_count": 33130,
  "input_risk_row_count": 33130,
  "input_strategy_row_count": 33130,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "REPLAY-DATA-A78 strict admission gate for A77 simulated-fill dataset only",
  "offline_fill_builder_only": true,
  "option_row_count": 25005,
  "orders_sent": false,
  "output_dataset_id": "fill_bearing_candidate_from_a77_20260510T154027Z",
  "output_dataset_root": "run/replay/parity/offline_materialization",
  "output_day_dir": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17",
  "output_execution_shadow_row_count": 33130,
  "output_profiles": {
    "execution_shadow_candidate.csv": {
      "breakdowns": {
        "execution_action_breakdown": {
          "no_order": 8125,
          "simulated_fill": 25005
        },
        "execution_status_breakdown": {
          "not_sent": 8125,
          "simulated_filled": 25005
        },
        "side_breakdown": {
          "quote_ticks_mme_fut_stream": 8125,
          "quote_ticks_mme_opt_stream": 25005
        }
      },
      "exists": true,
      "headers": [
        "ts_event",
        "symbol",
        "side",
        "execution_action",
        "execution_status",
        "order_sent",
        "orders_sent",
        "broker_call",
        "broker_calls_executed",
        "live_redis_write",
        "live_redis_writes_executed",
        "paper_or_live_enabled",
        "runtime_promotion",
        "engine_execution_performed",
        "qty",
        "order_qty",
        "filled_qty",
        "fill_price",
        "order_id",
        "position_effect",
        "execution_reason",
        "source_risk_row_index",
        "source_risk_sha256",
        "shadow_reconstruction",
        "created_at_utc",
        "offline_simulated_fill",
        "not_real_broker_fill",
        "simulation_fill_model",
        "fill_price_source",
        "simulated_dataset_batch",
        "source_strategy_action",
        "source_strategy_decision",
        "source_risk_status",
        "source_risk_decision",
        "source_risk_allowed"
      ],
      "nonzero_counts": {
        "fill_price": 25005,
        "filled_qty": 25005,
        "order_qty": 25005,
        "qty": 25005
      },
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/execution_shadow_candidate.csv",
      "row_count": 33130,
      "safety_true_counts": {},
      "sha256": "9067c766c5b20169d5e68eb949e2a669713f554e12715ec811abc610d96471b8",
      "size_bytes": 16357031,
      "truthy_counts": {
        "not_real_broker_fill": 33130,
        "offline_simulated_fill": 25005
      }
    },
    "quote_ticks_mme_fut_stream.csv": {
      "breakdowns": {},
      "exists": true,
      "headers": [
        "ts_event",
        "symbol",
        "bid",
        "ask",
        "ltp",
        "last",
        "price",
        "bid_qty",
        "ask_qty",
        "volume",
        "oi",
        "provider",
        "instrument_token",
        "source_stream",
        "source_ts_event_ns",
        "source_ts_exchange_ns",
        "source_ts_recv_ns",
        "selection_role",
        "validity",
        "validity_reason"
      ],
      "nonzero_counts": {},
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/quote_ticks_mme_fut_stream.csv",
      "row_count": 8125,
      "safety_true_counts": {},
      "sha256": "58b27e8518e22220189a9fbd27bc0680a2444e3dca6cff73b8afa98bd83bea65",
      "size_bytes": 1770628,
      "truthy_counts": {}
    },
    "quote_ticks_mme_opt_stream.csv": {
      "breakdowns": {},
      "exists": true,
      "headers": [
        "ts_event",
        "symbol",
        "bid",
        "ask",
        "ltp",
        "last",
        "price",
        "bid_qty",
        "ask_qty",
        "volume",
        "oi",
        "provider",
        "instrument_token",
        "source_stream",
        "source_ts_event_ns",
        "source_ts_exchange_ns",
        "source_ts_recv_ns",
        "selection_role",
        "validity",
        "validity_reason"
      ],
      "nonzero_counts": {},
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/quote_ticks_mme_opt_stream.csv",
      "row_count": 25005,
      "safety_true_counts": {},
      "sha256": "c34ff0859176c8c7249ecc5a6b92b3fb0b7587a9748965afc6ccd6d1f42378ed",
      "size_bytes": 5217596,
      "truthy_counts": {}
    },
    "risk_outputs_candidate.csv": {
      "breakdowns": {
        "action_breakdown": {
          "no_trade": 33130
        },
        "decision_breakdown": {
          "hold": 33130
        },
        "side_breakdown": {
          "quote_ticks_mme_fut_stream": 8125,
          "quote_ticks_mme_opt_stream": 25005
        }
      },
      "exists": true,
      "headers": [
        "ts_event",
        "symbol",
        "side",
        "action",
        "decision",
        "signal",
        "instrument_token",
        "source_stream",
        "risk_allowed",
        "allow",
        "approved",
        "risk_status",
        "risk_decision",
        "risk_reason",
        "order_intent",
        "order_qty",
        "max_qty",
        "risk_rule",
        "source_strategy_row_index",
        "source_strategy_sha256",
        "shadow_reconstruction"
      ],
      "nonzero_counts": {},
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/risk_outputs_candidate.csv",
      "row_count": 33130,
      "safety_true_counts": {},
      "sha256": "385554bb40d59ef63e569eeb7a72ba908b7eb90d0705ca4c8a77e16d7463c074",
      "size_bytes": 10635614,
      "truthy_counts": {}
    },
    "strategy_decisions_candidate.csv": {
      "breakdowns": {
        "action_breakdown": {
          "no_trade": 33130
        },
        "decision_breakdown": {
          "hold": 33130
        },
        "side_breakdown": {
          "quote_ticks_mme_fut_stream": 8125,
          "quote_ticks_mme_opt_stream": 25005
        }
      },
      "exists": true,
      "headers": [
        "ts_event",
        "symbol",
        "strategy",
        "decision",
        "action",
        "signal",
        "side",
        "confidence",
        "reason",
        "source_stream",
        "source_provider",
        "instrument_token",
        "source_bid",
        "source_ask",
        "source_ltp",
        "source_mid",
        "source_spread",
        "source_feature_row_index",
        "source_features_sha256"
      ],
      "nonzero_counts": {
        "source_ask": 33130,
        "source_bid": 33130,
        "source_ltp": 33130,
        "source_mid": 33130
      },
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/strategy_decisions_candidate.csv",
      "row_count": 33130,
      "safety_true_counts": {},
      "sha256": "5a9b8650cced23334ffedac6800fff3cadae215e3aa608426c3f7863d460f0f7",
      "size_bytes": 12240377,
      "truthy_counts": {}
    }
  },
  "output_single_day": "2026-04-17",
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "sample_fills": [
    {
      "fill_price": "187.05",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3537,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421122000000000"
    },
    {
      "fill_price": "136.55",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3538,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124200PE",
      "ts_event": "1776421122000000000"
    },
    {
      "fill_price": "187.4",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3539,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421122000000000"
    },
    {
      "fill_price": "118",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3540,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124150PE",
      "ts_event": "1776421123000000000"
    },
    {
      "fill_price": "187.4",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3541,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421123000000000"
    },
    {
      "fill_price": "136.7",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3542,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124200PE",
      "ts_event": "1776421123000000000"
    },
    {
      "fill_price": "216.975",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3543,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124200CE",
      "ts_event": "1776421123000000000"
    },
    {
      "fill_price": "118.025",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "row_index": 3546,
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "source_stream": "quote_ticks_mme_opt_stream",
      "symbol": "NIFTY2642124150PE",
      "ts_event": "1776421124000000000"
    }
  ],
  "simulated_fill_count": 25005,
  "source_a76": "run/proofs/proof_replay_data_a76_fill_build_contract_guarded_plan_20260510T153802Z.json",
  "verdict": "PASS_A77_OFFLINE_SIMULATED_FILL_DATASET_BUILT_NO_REPLAY_EXECUTION",
  "warning_count": 0,
  "warnings": []
}
