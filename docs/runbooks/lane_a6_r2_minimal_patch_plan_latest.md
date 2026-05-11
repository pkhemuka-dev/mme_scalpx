# A6-R2 — Minimal controlled-paper sandbox route patch plan

Generated IST: `2026-05-11T22:49:47.932497+05:30`

## Status

`PLAN_ONLY_NO_SOURCE_PATCH`

A6-R2 does not patch runtime. It only freezes the A6-R3 patch plan.

## Dependency from A6-R1

- A6-R1 final verdict: `BLOCKED_A6_R1_ROUTE_AUDIT_CONFIRMS_PATCH_PLAN_REQUIRED_NO_ORDER_NO_BROKER`
- A6-R1 route classification: `ROUTE_MISSING_OR_INCOMPLETE_STATICALLY_CONFIRMED`
- A6-R1 missing components:
  - `EXPLICIT_PAPER_SANDBOX_BROKER_BACKEND_NOT_DISCOVERED`
  - `EXECUTION_REAL_LIVE_FORBIDDEN_GUARD_NOT_CONFIRMED`

## Minimal patch targets for A6-R3 if approved

### 1. `app/mme_scalpx/integrations/broker_api.py`

Add an explicit controlled-paper sandbox backend seam:

- `ControlledPaperOrderRequest`
- `ControlledPaperOrderResult`
- `submit_controlled_paper_sandbox_order`

Required behavior:

- Never call Zerodha or Dhan real-live order APIs.
- Accept only `paper` or `sandbox`.
- Fail closed when no explicit paper/sandbox backend is active.
- Return metadata proving `broker_calls_executed=false`.
- Return metadata proving `order_sent=false` unless a verified paper/sandbox backend is active.

### 2. `app/mme_scalpx/services/execution.py`

Add hard controlled-paper entry guard before any order route:

- fail closed if real-live env is present
- fail closed if broker-order env is present without explicit paper/sandbox route
- fail closed if position is not flat
- fail closed if scope is not exactly one approved family/side
- fail closed if qty exceeds 1 lot
- fail closed if paper/sandbox backend is not discoverable
- never block exit/flatten safety paths

### 3. `app/mme_scalpx/services/controlled_paper_runtime.py`

Wire one-active-scope coordinator to execution preflight only:

- monitor all five strategies
- choose exactly one approved scoped signal
- no all-five simultaneous execution
- no strategy switching into execution
- no threshold relaxation
- no forced candidate

## A6-R3 proof requirements

- source backups
- py_compile proof
- fail-closed route proof
- no broker call
- no order
- `orders:mme:stream = 0`
- position remains `FLAT`
- milestone, runbook, sha256
