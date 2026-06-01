# A6-PAPER-R17M-R3C_read_only_execution_broker_requirement_static_fix_plan_after_r3b_no_patch_no_start_no_order_20260520_104712 Fix Plan

## Root cause

`execution.run(context)` exits because `context.broker` is missing during the observe-only no-broker R17M route.

## Required next patch

- Add a narrow observe-only/no-broker/report-only guard for execution runtime preflight.
- Guard must require `SCALPX_OBSERVE_ONLY=1`.
- Guard must require all paper/live/broker flags absent.
- Guard must not write orders.
- Normal execution behavior must remain fail-closed when those guard conditions are absent.

## Forbidden

- No real broker.
- No paper order.
- No risk/execution runtime retry in this batch.
- No Redis delete.

Proof: `run/proofs/A6-PAPER-R17M-R3C_read_only_execution_broker_requirement_static_fix_plan_after_r3b_no_patch_no_start_no_order_20260520_104712.json`
