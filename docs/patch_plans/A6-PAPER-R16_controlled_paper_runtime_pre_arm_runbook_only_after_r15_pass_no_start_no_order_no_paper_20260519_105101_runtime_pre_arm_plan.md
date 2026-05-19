# A6-PAPER-R16_controlled_paper_runtime_pre_arm_runbook_only_after_r15_pass_no_start_no_order_no_paper_20260519_105101

Verdict: `PASS_A6_PAPER_R16_RUNTIME_PRE_ARM_RUNBOOK_CREATED_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / controlled-paper runtime pre-arm runbook only.

## Boundary
- No paper order.
- No real live.
- No broker order.
- No real money.
- No risk/execution start.
- No source patch.
- No service start/stop.
- No Redis mutation.
- `orders:mme:stream` must remain 0.
- Position must remain FLAT.

## Required R17 gate warning

Previous live diagnosis found risk_pending_claim_error caused by unknown `XAUTOCLAIM`. R17 must not start risk/execution unless this Redis compatibility issue is proven safe, patched, or bypassed in a fail-closed way.

## Runtime pre-arm sequence
- Confirm pfeedcheck is HEALTHY_RECORDING.
- Confirm pstackcheck shows feeds/features/strategy running only.
- Confirm risk/execution are absent before arming preflight.
- Confirm lock:execution is absent.
- Confirm orders:mme:stream is 0.
- Confirm state:position:mme is FLAT.
- Confirm paper/live/broker env flags are unset.
- Confirm system:errors does not grow over a short check.
- Confirm Redis risk/execution consumer command compatibility, especially XAUTOCLAIM.
- Confirm controlled_paper_route guard import/matrix is still PASS.
- Only after future explicit approval, prepare scoped env for controlled-paper runtime.
- Do not place paper order in R17; R18 is earliest possible one-lot paper trial.

## Required environment model for future pre-arm
```json
{
  "always_forbidden_for_controlled_paper": [
    "SCALPX_REAL_LIVE_ALLOWED",
    "SCALPX_ALLOW_REAL_LIVE",
    "SCALPX_ALLOW_BROKER_ORDERS",
    "SCALPX_ENABLE_LIVE"
  ],
  "future_controlled_paper_only_candidates": [
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK=<exact scoped ack from controlled_paper_route.py>",
    "SCALPX_ENABLE_PAPER=1",
    "SCALPX_PAPER_ARMED=1"
  ],
  "must_be_unset_until_future_approval": [
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
    "SCALPX_PAPER_ARMED",
    "SCALPX_ENABLE_PAPER",
    "SCALPX_REAL_LIVE_ALLOWED",
    "SCALPX_ALLOW_REAL_LIVE",
    "SCALPX_ALLOW_BROKER_ORDERS",
    "SCALPX_ENABLE_LIVE"
  ]
}
```

## Kill / stop rules
- Stop immediately if orders:mme:stream becomes non-zero before final R18 approval.
- Stop immediately if state:position:mme is not FLAT before R18.
- Stop immediately if risk/execution start before their explicit approval.
- Stop immediately if lock:execution appears unexpectedly.
- Stop immediately if system:errors grows after starting any future service.
- Stop immediately if risk emits XAUTOCLAIM/consumer claim errors.
- Stop immediately if broker/live flags are present.
- Stop immediately if any real broker order id appears.
- Stop immediately if pfeedcheck loses HEALTHY_RECORDING.
- Stop immediately if pstackcheck shows anything beyond allowed scope.

## R17 gate blockers
- Redis XAUTOCLAIM unsupported or unknown command, unless code path is patched or safely bypassed.
- Any system:errors growth before pre-arm.
- Any non-zero orders stream before pre-arm.
- Any non-FLAT position before pre-arm.
- Any lock:execution before pre-arm.
- Any risk/execution process already running before approval.
- Any broker/live env flag present.
- Any missing R15 PASS / R16 PASS evidence.

## Current safety snapshot
```json
{
  "lock_execution_absent": true,
  "no_patch_no_start_no_stop_no_redis_mutation": true,
  "orders_xlen": 0,
  "orders_zero": true,
  "paper_live_flags_unset": true,
  "position_flat": true,
  "risk_execution_absent": true
}
```

## Redis compatibility probe
```json
{
  "command_info_xautoclaim_rc": 0,
  "command_info_xautoclaim_stderr": "",
  "command_info_xautoclaim_stdout": "",
  "xautoclaim_command_known": false
}
```

## Required next approval
```text
I APPROVE A6 CONTROLLED-PAPER RUNTIME ARMING PREFLIGHT ONLY: VERIFY CONTROLLED-PAPER ENV AND RISK/EXECUTION START CONDITIONS, NO PAPER ORDER YET, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, DO NOT START RISK/EXECUTION UNLESS ALL PREFLIGHT GATES PASS, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```