# R35B_R4O_dedup_position_pnl_no_replay_20260613_185030

classification: PASS_R35B_R4O_DEDUP_POSITION_PNL_EXPORTED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4O_dedup_position_pnl_no_replay_20260613_185030.json`
out_json: `run/audits/R35B_R4O_dedup_position_pnl_no_replay_20260613_185030/dedup_position_pnl_summary.json`
out_csv: `run/audits/R35B_R4O_dedup_position_pnl_no_replay_20260613_185030/dedup_position_trades.csv`

export_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## De-duplicated Position PnL summary
{
  "avg_pnl_points_per_position_proxy": 63.93750000000001,
  "by_action_count": {
    "ENTER_CALL": 2,
    "ENTER_PUT": 2
  },
  "by_action_pnl": {
    "ENTER_CALL": 393.5,
    "ENTER_PUT": -137.75
  },
  "dedup_position_trade_count_proxy": 4,
  "duplicates_ignored_total": 2904,
  "flat": 0,
  "important_limitation": "This is de-duplicated MTM proxy: first fill per symbol/action, exit at last replay LTP. It is closer to no-pyramiding paper logic but still not stop/target/time-exit lifecycle PnL.",
  "losses": 2,
  "method": "DEDUP_ONE_POSITION_PER_SYMBOL_ACTION_FIRST_ENTRY_TO_LAST_LTP",
  "paper_order": false,
  "pnl_total_points_proxy": 255.75000000000003,
  "positions": [
    {
      "dedup_qty": 1.0,
      "duplicate_entries_ignored": 1633,
      "entry_count_seen": 1634,
      "entry_execution_id": "execution_shadow_000018",
      "entry_price": 152.5,
      "entry_time": "2026-06-12T10:06:34Z",
      "exit_price_proxy": 363.85,
      "exit_time_proxy": "2026-06-12T15:30:01Z",
      "method": "DEDUP_ONE_POSITION_PER_SYMBOL_ACTION_FIRST_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": 211.35000000000002,
      "real_order": false,
      "risk_action": "ENTER_CALL",
      "side": "CALL",
      "symbol": "NIFTY2661623350CE"
    },
    {
      "dedup_qty": 1.0,
      "duplicate_entries_ignored": 1155,
      "entry_count_seen": 1156,
      "entry_execution_id": "execution_shadow_000024",
      "entry_price": 109.4,
      "entry_time": "2026-06-12T10:06:38Z",
      "exit_price_proxy": 30.0,
      "exit_time_proxy": "2026-06-12T15:31:24Z",
      "method": "DEDUP_ONE_POSITION_PER_SYMBOL_ACTION_FIRST_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": -79.4,
      "real_order": false,
      "risk_action": "ENTER_PUT",
      "side": "PUT",
      "symbol": "NIFTY2661623300PE"
    },
    {
      "dedup_qty": 1.0,
      "duplicate_entries_ignored": 59,
      "entry_count_seen": 60,
      "entry_execution_id": "execution_shadow_053537",
      "entry_price": 94.8,
      "entry_time": "2026-06-12T13:31:28Z",
      "exit_price_proxy": 36.45,
      "exit_time_proxy": "2026-06-12T15:30:01Z",
      "method": "DEDUP_ONE_POSITION_PER_SYMBOL_ACTION_FIRST_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": -58.349999999999994,
      "real_order": false,
      "risk_action": "ENTER_PUT",
      "side": "PUT",
      "symbol": "NIFTY2661623350PE"
    },
    {
      "dedup_qty": 1.0,
      "duplicate_entries_ignored": 57,
      "entry_count_seen": 58,
      "entry_execution_id": "execution_shadow_053540",
      "entry_price": 137.9,
      "entry_time": "2026-06-12T13:31:33Z",
      "exit_price_proxy": 320.05,
      "exit_time_proxy": "2026-06-12T15:31:24Z",
      "method": "DEDUP_ONE_POSITION_PER_SYMBOL_ACTION_FIRST_ENTRY_TO_LAST_LTP",
      "paper_order": false,
      "pnl_points_proxy": 182.15,
      "real_order": false,
      "risk_action": "ENTER_CALL",
      "side": "CALL",
      "symbol": "NIFTY2661623400CE"
    }
  ],
  "raw_filled_count": 2908,
  "real_order": false,
  "run_root": "run/replay/r35b_r4j/20260613_181431",
  "schema_version": "r35b_r4o_dedup_position_pnl_v1",
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
