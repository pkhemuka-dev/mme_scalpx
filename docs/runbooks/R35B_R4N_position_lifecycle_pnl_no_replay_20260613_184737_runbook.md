# R35B_R4N_position_lifecycle_pnl_no_replay_20260613_184737

classification: PASS_R35B_R4N_POSITION_LIFECYCLE_PNL_EXPORTED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4N_position_lifecycle_pnl_no_replay_20260613_184737.json`
out_json: `run/audits/R35B_R4N_position_lifecycle_pnl_no_replay_20260613_184737/position_lifecycle_pnl_summary.json`
out_csv: `run/audits/R35B_R4N_position_lifecycle_pnl_no_replay_20260613_184737/position_lifecycle_trades.csv`

export_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## Position lifecycle PnL summary
{
  "avg_pnl_points_per_position_proxy": 41434.46250000003,
  "by_action_count": {
    "ENTER_CALL": 2,
    "ENTER_PUT": 2
  },
  "by_action_pnl": {
    "ENTER_CALL": 239251.0000000002,
    "ENTER_PUT": -73513.15000000007
  },
  "flat": 0,
  "important_limitation": "This is still MTM proxy, but less inflated than per-fill PnL because repeated fills are grouped into one position per symbol/action.",
  "losses": 2,
  "method": "ONE_POSITION_PER_SYMBOL_ACTION_AVG_ENTRY_TO_LAST_LTP",
  "paper_order": false,
  "pnl_total_points_proxy": 165737.85000000012,
  "position_trade_count_proxy": 4,
  "positions": [
    {
      "avg_entry_price": 222.38004895960822,
      "entry_count": 1634,
      "exit_price_proxy": 363.85,
      "exit_time_proxy": "2026-06-12T15:30:01Z",
      "first_entry_time": "2026-06-12T10:06:34Z",
      "last_entry_time": "2026-06-12T15:29:15Z",
      "method": "ONE_POSITION_PER_SYMBOL_ACTION_AVG_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": 231161.9000000002,
      "real_order": false,
      "risk_action": "ENTER_CALL",
      "side": "CALL",
      "symbol": "NIFTY2661623350CE",
      "total_qty": 1634.0
    },
    {
      "avg_entry_price": 91.4071799307959,
      "entry_count": 1156,
      "exit_price_proxy": 30.0,
      "exit_time_proxy": "2026-06-12T15:31:24Z",
      "first_entry_time": "2026-06-12T10:06:38Z",
      "last_entry_time": "2026-06-12T15:30:00Z",
      "method": "ONE_POSITION_PER_SYMBOL_ACTION_AVG_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": -70986.70000000007,
      "real_order": false,
      "risk_action": "ENTER_PUT",
      "side": "PUT",
      "symbol": "NIFTY2661623300PE",
      "total_qty": 1156.0
    },
    {
      "avg_entry_price": 78.55749999999999,
      "entry_count": 60,
      "exit_price_proxy": 36.45,
      "exit_time_proxy": "2026-06-12T15:30:01Z",
      "first_entry_time": "2026-06-12T13:31:28Z",
      "last_entry_time": "2026-06-12T13:54:09Z",
      "method": "ONE_POSITION_PER_SYMBOL_ACTION_AVG_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": -2526.4499999999994,
      "real_order": false,
      "risk_action": "ENTER_PUT",
      "side": "PUT",
      "symbol": "NIFTY2661623350PE",
      "total_qty": 60.0
    },
    {
      "avg_entry_price": 180.58275862068962,
      "entry_count": 58,
      "exit_price_proxy": 320.05,
      "exit_time_proxy": "2026-06-12T15:31:24Z",
      "first_entry_time": "2026-06-12T13:31:33Z",
      "last_entry_time": "2026-06-12T13:52:05Z",
      "method": "ONE_POSITION_PER_SYMBOL_ACTION_AVG_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": 8089.100000000003,
      "real_order": false,
      "risk_action": "ENTER_CALL",
      "side": "CALL",
      "symbol": "NIFTY2661623400CE",
      "total_qty": 58.0
    }
  ],
  "raw_filled_count": 2908,
  "real_order": false,
  "run_root": "run/replay/r35b_r4j/20260613_181431",
  "schema_version": "r35b_r4n_position_lifecycle_pnl_v1",
  "selected_run_dir": "run/replay/r35b_r4j/20260613_181431/replay_locked_single_day_r35b_r4j_20260613_124433_7a2d5c32",
  "source_run_summary": {
    "candidate_count": 2946,
    "execution_shadow_filled_count": 2908,
    "pnl_total": null,
    "risk_action_breakdown": {
      "ENTER_CALL": 1692,
      "ENTER_PUT": 1216,
      "HOLD": 92608
    },
    "strategy_candidate_true_count": 2946,
    "trade_count": 0
  },
  "win_rate_proxy": 0.5,
  "wins": 2
}
## Export errors
