# A6-PAPER-R17B_read_only_risk_fallback_xpending_xclaim_syntax_diagnosis_no_patch_no_start_no_order_no_paper_20260519_141355

Verdict: `PASS_A6_PAPER_R17B_RISK_FALLBACK_SYNTAX_DIAGNOSIS_NO_PATCH_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / risk fallback syntax diagnosis only.

## Boundary
- No patch in R17B.
- No service start/stop.
- No Redis mutation.
- No risk/execution start.
- No paper order.
- No broker/live/real money.
- orders:mme:stream must remain 0.
- position must remain FLAT.

## Diagnosis
```json
{
  "helper_has_plain_xpending_execute_command_fallback": true,
  "helper_uses_xpending_range_idle_first": true,
  "likely_root_cause": "needs_manual_review",
  "plain_xpending_range_ok_for": [],
  "recommended_fix": "patch helper to catch broader Exception/ResponseError around xpending_range idle path and retry plain XPENDING - + count before publishing risk_pending_claim_error",
  "redis_version": "6.0.16",
  "xautoclaim_known": false,
  "xclaim_known": true,
  "xpending_idle_syntax_error_for": [],
  "xpending_known": true
}
```

## Patch-plan direction
- Keep patch target inside `app/mme_scalpx/services/risk.py` R16C-R2 helper region only.
- In `_a6_paper_r16c_r2_xpending_ids`, do not publish error immediately when `xpending_range(... idle=...)` raises Redis syntax error.
- Retry plain `XPENDING <stream> <group> - + <count>` using `execute_command`.
- Filter idle in Python when idle information is present; if idle information is absent, accept bounded IDs because XPENDING already returns pending IDs only.
- Keep XCLAIM path unchanged except for proof coverage.
- No broker/order/position/live/paper env changes.

## Required next approval
```text
I APPROVE A6 CONTROLLED-PAPER RISK FALLBACK SYNTAX PATCH PLAN ONLY: NO PATCH YET, NO PAPER ORDER, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```