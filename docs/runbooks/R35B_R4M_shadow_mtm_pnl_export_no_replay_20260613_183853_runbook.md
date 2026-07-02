# R35B_R4M_shadow_mtm_pnl_export_no_replay_20260613_183853

classification: PASS_R35B_R4M_SHADOW_MTM_PNL_EXPORTED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35B_R4M_shadow_mtm_pnl_export_no_replay_20260613_183853.json`
out_json: `run/audits/R35B_R4M_shadow_mtm_pnl_export_no_replay_20260613_183853/shadow_mtm_summary.json`
out_csv: `run/audits/R35B_R4M_shadow_mtm_pnl_export_no_replay_20260613_183853/shadow_mtm_trades.csv`

export_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## MTM summary
{
  "avg_pnl_points_proxy": 56.993758596974224,
  "by_action_count": {
    "ENTER_CALL": 1692,
    "ENTER_PUT": 1216
  },
  "by_action_pnl": {
    "ENTER_CALL": 239251.00000000105,
    "ENTER_PUT": -73513.15000000007
  },
  "by_symbol_count_top20": {
    "NIFTY2661623300PE": 1156,
    "NIFTY2661623350CE": 1634,
    "NIFTY2661623350PE": 60,
    "NIFTY2661623400CE": 58
  },
  "by_symbol_pnl_top20": {
    "NIFTY2661623300PE": -70986.70000000004,
    "NIFTY2661623350CE": 231161.90000000107,
    "NIFTY2661623350PE": -2526.45,
    "NIFTY2661623400CE": 8089.0999999999985
  },
  "flat": 1,
  "important_limitation": "This is mark-to-market proxy PnL using last replay LTP by symbol, not closed-trade lifecycle PnL.",
  "losses": 1235,
  "method": "MTM_TO_LAST_REPLAY_LTP_BY_SYMBOL",
  "paper_order": false,
  "pnl_total_points_proxy": 165737.85000000105,
  "real_order": false,
  "run_root": "run/replay/r35b_r4j/20260613_181431",
  "schema_version": "r35b_r4m_shadow_mtm_pnl_v1",
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
  "trade_count_proxy": 2908,
  "win_rate_proxy": 0.5749656121045392,
  "wins": 1672
}
## Export errors
