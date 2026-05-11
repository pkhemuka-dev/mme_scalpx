# REPLAY-DATA-A79 economics plumbing preview gate only

{
  "a80_preview_path": "run/replay/a79_economics_plumbing_preview_gate/20260510T154353Z/A80_ECONOMICS_PLUMBING_DRY_RUN_PREVIEW_DO_NOT_RUN.sh",
  "advisories": [
    "A79 is preview gate only. It validates that A80 can safely test economics plumbing schema on simulated fills.",
    "A80, if run later, must remain plumbing-only and must not claim strategy profitability.",
    "Real backtest remains blocked until a dataset has strategy-approved/risk-approved trade lifecycle evidence."
  ],
  "backtest_performed": false,
  "batch": "REPLAY-DATA-A79",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "ECONOMICS_PLUMBING_READY_FOR_A80_DRY_RUN_STRATEGY_BACKTEST_STILL_BLOCKED",
  "command_executed": false,
  "contract_id": "replay_fill_bearing_dataset_build_contract_v1",
  "dataset_admitted_for_backtest": false,
  "dataset_admitted_for_strategy_profit": false,
  "dataset_build_report_summary": {
    "fill_type": "offline_simulated_fill",
    "not_real_broker_fill": true,
    "row_counts": {
      "fill_price_nonzero_count": 25005,
      "filled_qty_nonzero_count": 25005,
      "futures_rows": 8125,
      "input_execution_shadow": 33130,
      "option_rows": 25005,
      "output_execution_shadow": 33130,
      "risk": 33130,
      "simulated_fill_count": 25005,
      "strategy": 33130
    },
    "simulation_scope": "economics_plumbing_probe_not_strategy_profit_claim"
  },
  "economics_plumbing_inputs_ready": true,
  "economics_plumbing_preview_gate_only": true,
  "economics_plumbing_preview_plan_generated": true,
  "economics_pnl_evaluation_allowed": false,
  "economics_pnl_evaluation_authorized": false,
  "economics_preview_generated": false,
  "execution_shadow_profile": {
    "breakdowns": {
      "execution_action_breakdown": {
        "no_order": 8125,
        "simulated_fill": 25005
      },
      "execution_status_breakdown": {
        "not_sent": 8125,
        "simulated_filled": 25005
      },
      "fill_price_source_breakdown": {
        "source_mid": 33130
      },
      "side_breakdown": {
        "quote_ticks_mme_fut_stream": 8125,
        "quote_ticks_mme_opt_stream": 25005
      },
      "source_risk_decision_breakdown": {
        "no_order": 33130
      },
      "source_risk_status_breakdown": {
        "risk_blocked": 33130
      },
      "source_strategy_action_breakdown": {
        "no_trade": 33130
      },
      "source_strategy_decision_breakdown": {
        "hold": 33130
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
    "sample_simulated_fill_rows": [
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "187.05",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124250CE",
        "ts_event": "1776421122000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "136.55",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124200PE",
        "ts_event": "1776421122000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "187.4",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124250CE",
        "ts_event": "1776421122000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "118",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124150PE",
        "ts_event": "1776421123000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "187.4",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124250CE",
        "ts_event": "1776421123000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "136.7",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124200PE",
        "ts_event": "1776421123000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "216.975",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124200CE",
        "ts_event": "1776421123000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "118.025",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124150PE",
        "ts_event": "1776421124000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "118.025",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124150PE",
        "ts_event": "1776421124000000000"
      },
      {
        "execution_action": "simulated_fill",
        "execution_status": "simulated_filled",
        "fill_price": "188.05",
        "fill_price_source": "source_mid",
        "filled_qty": "1",
        "side": "quote_ticks_mme_opt_stream",
        "source_risk_status": "risk_blocked",
        "source_strategy_action": "NO_TRADE",
        "symbol": "NIFTY2642124250CE",
        "ts_event": "1776421124000000000"
      }
    ],
    "sha256": "9067c766c5b20169d5e68eb949e2a669713f554e12715ec811abc610d96471b8",
    "size_bytes": 16357031,
    "truthy_counts": {
      "not_real_broker_fill": 33130,
      "offline_simulated_fill": 25005
    }
  },
  "execution_shadow_row_count": 33130,
  "file_status": {
    "dataset_build_report.json": {
      "exists": true,
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/dataset_build_report.json",
      "sha256": "f340717f1f7762897c8682aee33b7fa25a579a6c52a27867fd4b64a420283a1d",
      "size_bytes": 13032
    },
    "execution_shadow_candidate.csv": {
      "exists": true,
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/execution_shadow_candidate.csv",
      "sha256": "9067c766c5b20169d5e68eb949e2a669713f554e12715ec811abc610d96471b8",
      "size_bytes": 16357031
    },
    "fill_bearing_dataset_build_contract_v1.json": {
      "exists": true,
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/fill_bearing_dataset_build_contract_v1.json",
      "sha256": "1131d1e542676c5808057acf5bf21c62499b7636997555ae62951691b04876be",
      "size_bytes": 23153
    },
    "risk_outputs_candidate.csv": {
      "exists": true,
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/risk_outputs_candidate.csv",
      "sha256": "385554bb40d59ef63e569eeb7a72ba908b7eb90d0705ca4c8a77e16d7463c074",
      "size_bytes": 10635614
    },
    "source_manifest.json": {
      "exists": true,
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/source_manifest.json",
      "sha256": "ef55a272d16b0a80f36952bd8ecfbc93d61421a85b5c654449fb786fc522fae4",
      "size_bytes": 16177
    },
    "strategy_decisions_candidate.csv": {
      "exists": true,
      "path": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/strategy_decisions_candidate.csv",
      "sha256": "5a9b8650cced23334ffedac6800fff3cadae215e3aa608426c3f7863d460f0f7",
      "size_bytes": 12240377
    }
  },
  "fill_price_nonzero_count": 25005,
  "filled_qty_nonzero_count": 25005,
  "full_engine_replay_allowed": false,
  "full_system_execution_authorized": false,
  "full_system_preview_generated": false,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "REPLAY-DATA-A80 economics plumbing dry-run on simulated fills only",
  "not_real_broker_fill_true_count": 33130,
  "offline_simulated_fill_true_count": 25005,
  "orders_sent": false,
  "output_dataset_id": "fill_bearing_candidate_from_a77_20260510T154027Z",
  "output_day_dir": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17",
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "pnl_calculation_performed": false,
  "risk_profile": {
    "breakdowns": {
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
    "sample_simulated_fill_rows": [],
    "sha256": "385554bb40d59ef63e569eeb7a72ba908b7eb90d0705ca4c8a77e16d7463c074",
    "size_bytes": 10635614,
    "truthy_counts": {}
  },
  "risk_row_count": 33130,
  "sample_simulated_fill_rows": [
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "187.05",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421122000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "136.55",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124200PE",
      "ts_event": "1776421122000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "187.4",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421122000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "118",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124150PE",
      "ts_event": "1776421123000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "187.4",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421123000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "136.7",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124200PE",
      "ts_event": "1776421123000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "216.975",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124200CE",
      "ts_event": "1776421123000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "118.025",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124150PE",
      "ts_event": "1776421124000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "118.025",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124150PE",
      "ts_event": "1776421124000000000"
    },
    {
      "execution_action": "simulated_fill",
      "execution_status": "simulated_filled",
      "fill_price": "188.05",
      "fill_price_source": "source_mid",
      "filled_qty": "1",
      "side": "quote_ticks_mme_opt_stream",
      "source_risk_status": "risk_blocked",
      "source_strategy_action": "NO_TRADE",
      "symbol": "NIFTY2642124250CE",
      "ts_event": "1776421124000000000"
    }
  ],
  "source_a78": "run/proofs/proof_replay_data_a78_simulated_fill_dataset_admission_gate_20260510T154221Z.json",
  "source_manifest_summary": {
    "dataset_id": "fill_bearing_candidate_from_a77_20260510T154027Z",
    "materialization_type": "offline_simulated_fill_bearing_candidate",
    "not_real_broker_fill": true,
    "safety": {
      "broker_calls_executed": false,
      "engine_execution_performed": false,
      "live_redis_writes_executed": false,
      "not_real_broker_fill": true,
      "orders_sent": false,
      "paper_or_live_enabled": false,
      "services_started": false,
      "source_files_preserved": true
    }
  },
  "source_risk_status_breakdown": {
    "risk_blocked": 33130
  },
  "source_strategy_action_breakdown": {
    "no_trade": 33130
  },
  "strategy_profile": {
    "breakdowns": {
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
    "sample_simulated_fill_rows": [],
    "sha256": "5a9b8650cced23334ffedac6800fff3cadae215e3aa608426c3f7863d460f0f7",
    "size_bytes": 12240377,
    "truthy_counts": {}
  },
  "strategy_row_count": 33130,
  "verdict": "PASS_A79_ECONOMICS_PLUMBING_PREVIEW_GATE_NO_PNL",
  "warning_count": 2,
  "warnings": [
    "Dataset is admitted only for economics plumbing; source strategy/risk remained NO_TRADE/risk_blocked.",
    "A79 does not compute PnL and does not approve strategy-profit backtesting."
  ]
}
