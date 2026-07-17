# R38QT_R31_R2_SHADOW_DECISION_TO_PRICE_JOIN_LIFECYCLE_PNL_ANALYSIS_NO_ORDER_20260708_222055

## Purpose
Decision-to-price joined shadow lifecycle analytics.

## Final verdict
REVIEW_R38QT_R31_R2_DECISION_PRICE_JOIN_ANALYSIS_HAS_DATA_GAPS_NO_ORDER

Failed gates: ['price_streams_found', 'joined_price_events_seen']

## Decision counts
Events: 7520
Family counts: {'MIST': 7520}
Action counts: {'HOLD': 1682, 'ENTER_PUT': 5838}
Shadow-present events: 5838

## Price join
Price streams found: 0
Tick keys loaded: 0
Joined price events: 0

## Virtual lifecycle
Lifecycle segments: 0
Closed virtual trades with joined price: 0
Wins/Losses/Flat: 0 / 0 / 0
Win rate %: None
Total virtual PnL one-lot: None
Best/Worst virtual trade: None / None
Avg/Median duration sec: None / None
Selector switches: 0

## Safety
No broker, no order, no paper/live, no risk/execution, no Redis write.

## Important
Research PnL only. Not broker PnL.
