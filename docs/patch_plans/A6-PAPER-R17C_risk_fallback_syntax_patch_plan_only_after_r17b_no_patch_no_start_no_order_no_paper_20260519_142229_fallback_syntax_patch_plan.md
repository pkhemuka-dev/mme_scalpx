# A6-PAPER-R17C_risk_fallback_syntax_patch_plan_only_after_r17b_no_patch_no_start_no_order_no_paper_20260519_142229

Verdict: `PASS_A6_PAPER_R17C_RISK_FALLBACK_SYNTAX_PATCH_PLAN_CREATED_NO_PATCH_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / risk fallback syntax patch plan only.

## Boundary
- No source patch in R17C.
- No service start/stop.
- No Redis mutation.
- No risk/execution start.
- No paper order.
- No broker/live/real money.
- orders:mme:stream must remain 0.
- position must remain FLAT.

## Consumed diagnosis
```json
{
  "r17b_diagnosis": {
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
  },
  "r17b_verdict": "PASS_A6_PAPER_R17B_RISK_FALLBACK_SYNTAX_DIAGNOSIS_NO_PATCH_NO_START_NO_ORDER_NO_PAPER",
  "redis_version_now": "6.0.16",
  "xautoclaim_known_now": false,
  "xclaim_known_now": true,
  "xpending_known_now": true
}
```

## Patch design
```json
{
  "acceptance_tests_after_source_patch": [
    "Compile risk.py.",
    "Import matrix: idle xpending_range success path.",
    "Import matrix: idle syntax failure -> plain xpending_range success.",
    "Import matrix: idle and redis-py range failure -> execute_command XPENDING success.",
    "Import matrix: all XPENDING fallback failure -> empty result + bounded risk_pending_claim_error via _batch14_claim_pending.",
    "AST audit: patch marker present, target function present, no broker/order/position/live env fragments in patch region.",
    "No-start safety proof: orders=0, position=FLAT, risk/execution absent, lock:execution absent, errors stable."
  ],
  "do_not_touch": [
    "execution.py",
    "broker_api.py",
    "strategy.py",
    "order placement paths",
    "position mutation paths",
    "paper/live/broker env gates"
  ],
  "patch_required": true,
  "primary_target": "app/mme_scalpx/services/risk.py",
  "problem_being_fixed": [
    "R17 produced risk_pending_claim_error with Redis ResponseError: syntax error for trades:ledger:stream and cmd:mme:stream.",
    "R17B confirmed Redis 6.0.16, XAUTOCLAIM unavailable, XPENDING/XCLAIM available.",
    "The R16C-R2 helper tries redis-py xpending_range(... idle=int(min_idle_ms)) first.",
    "Fallback must not publish risk_pending_claim_error until plain XPENDING fallback has been attempted."
  ],
  "r17_retry_rule": "Do not retry R17 until R17D source patch, R17E static proof, and R17F no-start safety proof pass.",
  "required_patch_behavior": [
    "Inside _a6_paper_r16c_r2_xpending_ids, wrap the xpending_range(... idle=...) branch in broad Exception handling.",
    "If idle branch fails with ResponseError/syntax error/TypeError/unsupported syntax, retry plain xpending_range(stream, group, '-', '+', count).",
    "If redis-py xpending_range remains unusable, use execute_command('XPENDING', stream_name, group_name, '-', '+', count).",
    "Normalize pending rows through existing _a6_paper_r16c_r2_pending_ids_from_xpending_rows.",
    "Do not publish risk_pending_claim_error from _xpending_ids itself.",
    "Let _batch14_claim_pending publish a bounded risk_pending_claim_error only if both XPENDING fallback and XCLAIM path fail.",
    "Keep _a6_paper_r16c_r2_xclaim unchanged unless static proof shows it also needs syntax fallback."
  ],
  "target_function": "_a6_paper_r16c_r2_xpending_ids"
}
```

## Source helper context
```json
{
  "function_names": [
    "_a6_paper_r16c_r2_pending_ids_from_xpending_rows",
    "_a6_paper_r16c_r2_xclaim",
    "_a6_paper_r16c_r2_xpending_ids",
    "_batch14_claim_pending"
  ],
  "has_no_safe_path_error": true,
  "has_plain_xpending_execute_command": true,
  "has_xclaim_execute_command": false,
  "has_xpending_range_idle": true,
  "sha256": "87a14f62f041038e55615f365f2a4b12d76067d1ab6c93b60945807813d7ba3d"
}
```

## Required next approval
```text
I APPROVE A6 CONTROLLED-PAPER RISK FALLBACK SYNTAX SOURCE PATCH ONLY: PATCH _a6_paper_r16c_r2_xpending_ids RETRY-PLAIN-XPENDING PATH ONLY, NO PAPER ORDER, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```