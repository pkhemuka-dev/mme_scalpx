# REPLAY-DATA-A81 economics plumbing artifact audit / stop

{
  "advisories": [
    "Lane E A-series can safely stop here for simulated-fill economics plumbing.",
    "Next valid future work is a new dataset-capture/build lane for true strategy-approved/risk-approved trades, not more PnL on this simulated NO_TRADE/risk_blocked dataset."
  ],
  "artifact_audit_only": true,
  "artifact_status": {
    "coverage_json": {
      "exists": true,
      "expected_sha256": "a5ede2ecfdb7256fe9b46320682011b838144393054a93f5ec4e17ae69dd1737",
      "path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_coverage.json",
      "sha256": "a5ede2ecfdb7256fe9b46320682011b838144393054a93f5ec4e17ae69dd1737",
      "size_bytes": 624
    },
    "economics_rows_csv": {
      "exists": true,
      "expected_sha256": "b96043ccae512930b696744059433c306a1bfbad21fd3e63ccfab834e910db3c",
      "path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_rows.csv",
      "sha256": "b96043ccae512930b696744059433c306a1bfbad21fd3e63ccfab834e910db3c",
      "size_bytes": 4312759
    },
    "sample_rows_json": {
      "exists": true,
      "expected_sha256": "f1b292c7604d92f04e55ca5ca39f3d4d8244b6da9b9fc13becead8e3339d8fc4",
      "path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_sample_rows.json",
      "sha256": "f1b292c7604d92f04e55ca5ca39f3d4d8244b6da9b9fc13becead8e3339d8fc4",
      "size_bytes": 11606
    },
    "schema_preview_json": {
      "exists": true,
      "expected_sha256": "7ce27c0552b5bc6f9f37308aa0f4aecf26efcab0f2f71bbc5c78857bf0619c20",
      "path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_schema_preview.json",
      "sha256": "7ce27c0552b5bc6f9f37308aa0f4aecf26efcab0f2f71bbc5c78857bf0619c20",
      "size_bytes": 1268
    },
    "summary_json": {
      "exists": true,
      "expected_sha256": "a97b7fbe8391e02b7a9602cb91b95721730bdff9608f89731de24c915e2542e0",
      "path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_summary.json",
      "sha256": "a97b7fbe8391e02b7a9602cb91b95721730bdff9608f89731de24c915e2542e0",
      "size_bytes": 779
    }
  },
  "backtest_performed": false,
  "batch": "REPLAY-DATA-A81",
  "blocker_count": 0,
  "blockers": [],
  "broker_calls_executed": false,
  "classification": "PLUMBING_ARTIFACTS_VALIDATED_STOP_BACKTEST_STILL_BLOCKED",
  "command_executed": false,
  "coverage": {
    "execution_action_breakdown": {
      "no_order": 8125,
      "simulated_fill": 25005
    },
    "execution_status_breakdown": {
      "not_sent": 8125,
      "simulated_filled": 25005
    },
    "fill_price_nonzero_count": 25005,
    "fill_price_source_breakdown": {
      "source_mid": 33130
    },
    "filled_qty_nonzero_count": 25005,
    "gross_fill_notional_not_pnl": "4026378.800",
    "not_real_broker_true_count": 33130,
    "row_count": 33130,
    "safety_true_counts": {},
    "simulated_fill_rows": 25005,
    "source_risk_status_breakdown": {
      "risk_blocked": 33130
    },
    "source_strategy_action_breakdown": {
      "no_trade": 33130
    }
  },
  "dataset_admitted_for_backtest": false,
  "dataset_admitted_for_real_fill_economics": false,
  "dataset_admitted_for_strategy_profit": false,
  "economics_pnl_evaluation_allowed": false,
  "full_engine_replay_allowed": false,
  "gross_fill_notional_is_not_pnl": true,
  "live_redis_writes_executed": false,
  "live_trading_approved": false,
  "new_replay_execution_started": false,
  "next_batch": "STOP_LANE_E_SIMULATED_FILL_PLUMBING_COMPLETE_TRUE_BACKTEST_REQUIRES_STRATEGY_RISK_APPROVED_TRADE_DATASET",
  "orders_sent": false,
  "paper_armed_approved": false,
  "paper_or_live_enabled": false,
  "pnl_calculation_performed": false,
  "rows_profile": {
    "exists": true,
    "headers": [
      "ts_event",
      "symbol",
      "side",
      "filled_qty",
      "fill_price",
      "gross_fill_notional",
      "fill_price_source",
      "offline_simulated_fill",
      "not_real_broker_fill",
      "source_strategy_action",
      "source_strategy_decision",
      "source_risk_status",
      "source_risk_decision",
      "plumbing_scope"
    ],
    "path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_rows.csv",
    "row_count": 25005,
    "scope_breakdown": {
      "simulated_fill_mechanics_not_pnl": 25005
    },
    "sha256": "b96043ccae512930b696744059433c306a1bfbad21fd3e63ccfab834e910db3c",
    "size_bytes": 4312759,
    "source_risk_status_breakdown": {
      "risk_blocked": 25005
    },
    "source_strategy_action_breakdown": {
      "no_trade": 25005
    }
  },
  "sample_row_count": 20,
  "schema": {
    "batch": "REPLAY-DATA-A80",
    "columns": [
      "ts_event",
      "symbol",
      "side",
      "filled_qty",
      "fill_price",
      "gross_fill_notional",
      "fill_price_source",
      "offline_simulated_fill",
      "not_real_broker_fill",
      "source_strategy_action",
      "source_strategy_decision",
      "source_risk_status",
      "source_risk_decision",
      "plumbing_scope"
    ],
    "forbidden_interpretations": [
      "not strategy-profit backtest",
      "not real broker fill economics",
      "not PnL evaluation",
      "not paper/live approval"
    ],
    "input_file": "run/replay/parity/offline_materialization/fill_bearing_candidate_from_a77_20260510T154027Z/2026-04-17/execution_shadow_candidate.csv",
    "output_file": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_rows.csv",
    "required_input_columns": [
      "ts_event",
      "symbol",
      "side",
      "execution_action",
      "execution_status",
      "filled_qty",
      "fill_price",
      "offline_simulated_fill",
      "not_real_broker_fill",
      "fill_price_source",
      "source_strategy_action",
      "source_strategy_decision",
      "source_risk_status",
      "source_risk_decision"
    ],
    "schema_name": "economics_plumbing_rows_v1",
    "scope": "simulated_fill_mechanics_not_pnl"
  },
  "source_a80": "run/proofs/proof_replay_data_a80_economics_plumbing_dry_run_20260510T154623Z.json",
  "summary": {
    "backtest_performed": false,
    "batch": "REPLAY-DATA-A80",
    "coverage_path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_coverage.json",
    "economics_rows_path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_rows.csv",
    "gross_fill_notional_is_not_pnl": true,
    "gross_fill_notional_not_pnl": "4026378.800",
    "plumbing_dry_run_ok": true,
    "pnl_calculation_performed": false,
    "row_count": 33130,
    "sample_path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_sample_rows.json",
    "schema_path": "run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_schema_preview.json",
    "simulated_fill_rows": 25005
  },
  "verdict": "PASS_A81_ECONOMICS_PLUMBING_ARTIFACT_AUDIT_STOP",
  "warning_count": 2,
  "warnings": [
    "A81 confirms A80 artifacts are plumbing-only and not PnL/backtest outputs.",
    "Strategy-profit backtesting remains blocked until a true strategy-approved and risk-approved trade lifecycle dataset exists."
  ]
}
