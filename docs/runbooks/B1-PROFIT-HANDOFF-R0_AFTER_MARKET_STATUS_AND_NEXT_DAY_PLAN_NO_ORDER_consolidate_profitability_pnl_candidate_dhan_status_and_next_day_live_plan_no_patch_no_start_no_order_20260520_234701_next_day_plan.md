# B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701 Next-Day Plan

No after-market order. No broker. No paper. No start/stop in this batch.

## Tomorrow live session

- Do not run paper order first.
- During live session, verify pfeeds/pstack live growth: Zerodha futures, selected option, features, decisions.
- Run candidate audit: need candidate_count >= 1 before paper preflight.
- In parallel, restore/verify Dhan context growth: opt_selected_dhan and opt_context_dhan must grow for full-family/MISO testing.
- Only after candidate_count >= 1: run controlled paper preflight.
- Only after explicit approval: one paper trial, no real broker/live.

Proof: `run/proofs/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701.json`
