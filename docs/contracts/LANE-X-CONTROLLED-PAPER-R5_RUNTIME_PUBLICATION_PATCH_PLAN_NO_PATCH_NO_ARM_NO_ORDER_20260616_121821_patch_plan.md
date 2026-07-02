# LANE-X-CONTROLLED-PAPER-R5_RUNTIME_PUBLICATION_PATCH_PLAN_NO_PATCH_NO_ARM_NO_ORDER_20260616_121821

## Current conclusion

Controlled paper is NOT ready to arm.

R4 proved that source writers and controlled-paper logic exist, but runtime publication is missing.

## What is working

- Live observe-only process is running.
- Live market data is visible.
- Source has position-state writer logic.
- Source has risk-state writer logic.
- Source has execution-state writer logic.
- Source has controlled-paper / route-gate logic.

## What is missing

Runtime does not publish the required controlled-paper gate state:

- state:position / flat proof is not visible.
- state:risk / controlled-paper veto proof is not visible.
- paper gate / pstatus / route status is not visible.
- pstatus / paper_status helper is not visible.

## Required after-market patch/harness

Create a fail-closed status publication path that exposes:

### 1. Position state

- has_position = 0
- position_side = FLAT
- qty_lots = 0
- qty_units = 0

### 2. Risk state

- reason_code = CONTROLLED_PAPER_NOT_ARMED
- controlled_paper_entry_veto = 1
- position_open = 0
- trades_today = 0
- day_realized_pnl = 0

### 3. Execution state

- entry_pending = 0
- exit_pending = 0
- pending_order_json empty
- last_error empty

### 4. Paper gate verdict

- paper_armed = false by default
- route_allowed = false until explicit arming
- paper_status or pstatus proof visible

## Before any paper trial

Must pass these, in order:

1. Static compile/import.
2. No-order fixture.
3. Runtime observe-only publication proof.
4. Controlled-paper gate verdict proof.
5. Explicit user approval for a separate arming command.
6. One-lot micro paper trial only.

## Safety

No paper was armed.
No broker order was sent.
No risk service was started.
No execution service was started.
No Redis key was deleted.
No source patch was done in this step.
