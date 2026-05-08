# Milestone — Batch RAW-R Family PnL and Gap Review

Date: 2026-05-01
Generated UTC: 2026-05-01T09:08:07.769450+00:00
Batch tag: batch_raw_r_family_pnl_gap_review_freeze_final_20260501_143807

Achieved:
- Produced family-level PnL review from RAW-Q evidence.
- Produced unknown trade source gap map.
- Produced likely producer gap summary.
- Kept promotion/paper/live blocked.

Review result:
- review_verdict: FAMILY_RANKING_READY_PARTIAL_COVERAGE
- trade_count: 66
- known_family_trade_count: 15
- unknown_family_trade_count: 51
- unknown_family_ratio: 0.772727
- rank_candidate_family_count: 5
- best_family: {'expectancy': 206.25, 'family': 'MISB', 'flat_trades': 0, 'gross_pnl': 618.75, 'losing_trades': 0, 'net_pnl_after_costs': 618.75, 'profit_factor': None, 'trade_count': 3, 'win_rate': 1.0, 'winning_trades': 3}
- worst_family: {'expectancy': 206.25, 'family': 'MIST', 'flat_trades': 0, 'gross_pnl': 618.75, 'losing_trades': 0, 'net_pnl_after_costs': 618.75, 'profit_factor': None, 'trade_count': 3, 'win_rate': 1.0, 'winning_trades': 3}

Next:
Patch original replay trade/candidate producers to emit family/side/strategy_id at creation time, then rerun larger replay-only evidence.
