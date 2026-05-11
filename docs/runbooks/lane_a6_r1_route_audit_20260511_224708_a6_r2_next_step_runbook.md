# lane_a6_r1_route_audit_20260511_224708 — A6-R2 next-step runbook

## Current Lane A6 status

A6-R1 route audit completed with verdict:

`BLOCKED_A6_R1_ROUTE_AUDIT_CONFIRMS_PATCH_PLAN_REQUIRED_NO_ORDER_NO_BROKER`

Route classification:

`ROUTE_MISSING_OR_INCOMPLETE_STATICALLY_CONFIRMED`

## Missing components

- `EXPLICIT_PAPER_SANDBOX_BROKER_BACKEND_NOT_DISCOVERED`
- `EXECUTION_REAL_LIVE_FORBIDDEN_GUARD_NOT_CONFIRMED`

## Next batch

`A6-R2 minimal explicit controlled-paper sandbox route patch plan / no source patch yet`

## If A6-R2 is patch-plan mode

A6-R2 must produce a minimal patch plan only. It must not patch source yet. It must specify:

1. exact file owner for controlled-paper coordinator
2. exact file owner for execution hard guard
3. exact broker/paper backend seam
4. exact one-active-scope selector contract
5. exact fail-closed behavior when paper backend/tool is absent
6. proof plan for no order, no broker call, orders stream zero, position flat
7. compile/import proof scope
8. tomorrow live-session runbook impact

## If A6-R2 is route-discovery proof mode

A6-R2 must prove the route is discoverable and fail-closed without:

- source patch
- service start
- risk/execution start
- paper/live enablement
- broker call
- order creation
- Redis trading-stream write

## Hard prohibitions remain

- no real live
- no broker call
- no order placement
- no paper/live enablement
- no all-5 simultaneous execution
- no automatic strategy switching into execution
- no threshold relaxation
- no forced candidate
- no reuse of old approval phrases
