# lane_a6_r0_proof_reconciliation_20260511_223030 — Next route audit runbook

## Current status

Controlled paper remains BLOCKED. Real live remains BLOCKED. No order was attempted. No broker call was executed.

## A6-R0 canonical blocker

`EXPLICIT_CONTROLLED_PAPER_ORDER_TOOL_NOT_FOUND_FAIL_CLOSED`

Canonical Lane A6 blocker is the missing explicit controlled-paper/sandbox order-cycle route. MARKET_WINDOW_NOT_OPEN belongs to a separate MISR CALL attempt; SCOPE_SIGNAL_NOT_PRESENT belongs to natural no-signal windows and does not resolve the route gap.

## Required next batch: A6-R1

A6-R1 must perform controlled-paper order-cycle route audit only. It must inspect, without patching:

1. `app/mme_scalpx/services/execution.py`
2. `app/mme_scalpx/services/risk.py`
3. `app/mme_scalpx/integrations/broker_api.py`
4. `app/mme_scalpx/integrations/provider_runtime.py`
5. `app/mme_scalpx/core/names.py`
6. `app/mme_scalpx/services/strategy.py`
7. related configs, contracts, runbooks, proof JSONs, and producer/consumer paths

## Hard prohibitions

- No real live
- No broker call
- No order placement
- No paper/live enablement
- No risk/execution live start
- No all-family execution carrier
- No threshold relaxation
- No source patch in A6-R1 unless A6-R1 is explicitly converted into a user-approved patch batch later

## A6-R1 output requirement

A6-R1 must decide one of:

- route exists and is fail-closed/discoverable, or
- route missing and A6-R2 should prepare a minimal explicit controlled-paper/sandbox patch plan, or
- evidence/proof shape is insufficient and a diagnostic batch is required.
