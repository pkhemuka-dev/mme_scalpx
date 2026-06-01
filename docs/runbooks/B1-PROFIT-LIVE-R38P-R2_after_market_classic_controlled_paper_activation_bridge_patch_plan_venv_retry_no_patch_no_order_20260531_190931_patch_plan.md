# B1-PROFIT-LIVE-R38P-R2_after_market_classic_controlled_paper_activation_bridge_patch_plan_venv_retry_no_patch_no_order_20260531_190931 patch plan

## Objective
Prepare the smallest possible path from observe-only classic candidate to controlled-paper promotion.

## R38R doctrine
Classic-family controlled paper may promote only when all conditions are true:

1. `SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1`
2. exact scope ack present
3. family in `MIST/MISB/MISC/MISR`
4. side in `CALL/PUT`
5. max lot = 1
6. candidate is genuinely entry-eligible
7. Zerodha execution only
8. Dhan execution disabled
9. MISO blocked unless Dhan context is healthy
10. no active position
11. orders/risk/execution streams zero before arming
12. no real live
13. no threshold relaxation
14. no automatic paper without explicit approval

## Proposed R38R patch shape
- Add/repair a narrow activation bridge path that can mark eligible classic family surface as `activation_safe_to_promote=true` only under explicit controlled-paper env/scope.
- Preserve `live_orders_allowed=false` unless later risk/execution controlled-paper batch explicitly owns order routing.
- Keep execution/risk untouched.
- Add fixture proof:
  - no env -> no promote
  - wrong ack -> no promote
  - MISO + no Dhan -> no promote
  - classic + env + eligible -> promote marker true
  - classic + env + not eligible -> no promote
