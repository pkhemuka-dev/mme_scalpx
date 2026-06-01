# B1-PROFIT-LIVE-R38P-R2_after_market_classic_controlled_paper_activation_bridge_patch_plan_venv_retry_no_patch_no_order_20260531_190931

## Verdict
`PASS_R38P_R2_TINY_CLASSIC_ACTIVATION_PATCH_PLAN_READY_NO_PATCH`

## Meaning
R38P-R2 is an after-market patch-plan batch only. No patch was applied.

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_feeds: ``
- lock_execution: ``
- pauto_stopped: `True`
- pseal_pass: `True`
- latest_handoff_present: `True`
- no_live_processes: `True`

## Imports
`{'app.mme_scalpx.services.controlled_paper_route': 'OK', 'app.mme_scalpx.services.controlled_paper_runtime': 'OK', 'app.mme_scalpx.services.execution': 'OK', 'app.mme_scalpx.services.risk': 'OK', 'app.mme_scalpx.services.strategy': 'OK', 'app.mme_scalpx.services.strategy_family.activation': 'OK'}`

## Source authority
- strategy activation gate: `True`
- controlled_paper_truth: `True`
- scope selector: `True`
- order cycle builder: `True`
- safe_to_promote: `True`
- live_orders_allowed: `True`
- env gates: `True`
- classic_runtime_disabled: `True`
- MISO/Dhan law evidence: `True`

## Minimal patch surface for R38R
1. `app/mme_scalpx/services/strategy.py`
2. `app/mme_scalpx/services/strategy_family/activation.py`
3. `app/mme_scalpx/services/controlled_paper_runtime.py`

## Do not touch in R38R
- execution/risk services
- provider runtime
- feeds
- Dhan deep-fix
- strategy thresholds
- broker/live routing


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
