# RAW-R Family PnL and Producer-Source Gap Review

Generated UTC: 2026-05-01T09:08:14.961029+00:00

## Verdict
- review_verdict: FAMILY_RANKING_READY_PARTIAL_COVERAGE
- promotion_allowed: False
- paper_live_allowed: False

## Family PnL
- MISB: trades=3, net=618.75, expectancy=206.25, win_rate=1.0
- MISC: trades=3, net=618.75, expectancy=206.25, win_rate=1.0
- MISO: trades=3, net=618.75, expectancy=206.25, win_rate=1.0
- MISR: trades=3, net=618.75, expectancy=206.25, win_rate=1.0
- MIST: trades=3, net=618.75, expectancy=206.25, win_rate=1.0
- UNKNOWN: trades=51, net=3748.5, expectancy=73.5, win_rate=0.588235

## Coverage
- trade_count: 66
- known_family_trade_count: 15
- unknown_family_trade_count: 51
- unknown_family_ratio: 0.772727
- rank_candidate_family_count: 5

## Likely producer gaps
- app/mme_scalpx/replay/reports.py or app/mme_scalpx/replay/artifacts.py: 51 unknown trades
  - fix: Emit family, side, strategy_id into trade/candidate rows at artifact creation time.

## Governance
RAW-R is review-only. It does not enable paper/live and does not mutate production.
