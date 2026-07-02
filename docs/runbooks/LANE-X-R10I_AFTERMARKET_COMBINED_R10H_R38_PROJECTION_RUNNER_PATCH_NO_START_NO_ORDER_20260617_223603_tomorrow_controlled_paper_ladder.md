# LANE-X-R10I_AFTERMARKET_COMBINED_R10H_R38_PROJECTION_RUNNER_PATCH_NO_START_NO_ORDER_20260617_223603 — Tomorrow Controlled-Paper Combined Plan

## Purpose
Combine R10H safety repair with R38 projection/timing learning.

## Do not run after-market
- Do not start runtime tonight.
- Do not arm paper tonight.
- Do not place broker/live order.

## Tomorrow sequence
1. Run:
   ```bash
   bash bin/r10i_tomorrow_combined_r10h_r38_preflight_no_start.sh
   ```

2. If clean and market live, give exact approval:
   ```bash
   export R10J_ONE_LOT_CONTROLLED_PAPER_ACK="I APPROVE R10J ONE-LOT CONTROLLED PAPER ONLY: NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, MAX ONE PROJECTED ENTER OR PAPER EVENT, STOP AND FREEZE EVIDENCE"
   bash bin/r10j_tomorrow_one_lot_controlled_paper_wrapper_requires_fresh_approval.sh
   ```

## Required proof
- `r38ee_projection_projected=1`
- top-level `ENTER_CALL` or `ENTER_PUT`
- `qty=1`
- risk stream increment
- execution stream increment
- paper/trade event or clean blocker
- stop/freeze after first event

## Safety
- R10H Redis `noeviction` required.
- strict FLAT position hash required.
- pstatus must allow route.
- no real live.
- no broker order.
- max one event.
