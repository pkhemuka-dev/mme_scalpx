# LANE-B-R5_FIND_VALID_CANDIDATE_OR_PATCH_IMPACT_REPLAY_ROUTE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_143108

If VALID_CANDIDATE_OR_FILL found:
- Next: run strategy-wise PnL audit on that existing replay run.
- No patch.

If NO_EXISTING_FILL_RUN found:
- Next: choose controlled route:
  1. baseline-vs-shadow patch-impact replay using Lane X patch surface, or
  2. wait for / build a valid candidate dataset.
- Do not force candidates or tune thresholds blindly.
