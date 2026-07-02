# LANE-MIV-LIVE-R7G_TOP40_ROBUSTNESS_AND_PNL_TIEBREAKER_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_104030 — R7F Corrected Truth Freeze

R7F is frozen as corrected source of truth.

Key facts:
- R7D/R7E candidate_id join was invalid because candidate_id was blank for all 5,296 rows.
- Correct join method: row_order.
- Correct all-candidate summary matches R7C:
  - win_pct 32.6662%
  - avg_return_pct 0.131631%
  - net_shadow_pnl_pct 697.115817%
- Corrected top40 score result is strong, but R7G must verify no future-PnL tie-break leak before any throttle design.

R7F proof:
- run/proofs/LANE-MIV-LIVE-R7F_CORRECTED_RANK_QUALITY_ROW_ORDER_JOIN_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_103628.json
