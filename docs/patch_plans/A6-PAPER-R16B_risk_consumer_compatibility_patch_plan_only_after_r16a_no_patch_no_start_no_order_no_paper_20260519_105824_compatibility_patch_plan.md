# A6-PAPER-R16B_risk_consumer_compatibility_patch_plan_only_after_r16a_no_patch_no_start_no_order_no_paper_20260519_105824

Verdict: `PASS_A6_PAPER_R16B_RISK_CONSUMER_COMPATIBILITY_PATCH_PLAN_CREATED_NO_PATCH_NO_START_NO_ORDER_NO_PAPER`

Lane: A6-PAPER / risk consumer compatibility patch plan only.

## Boundary
- No patch in R16B.
- No service start/stop.
- No Redis mutation.
- No risk/execution start.
- No paper order.
- No real live.
- No broker order.
- No real money.
- `orders:mme:stream` must remain 0.
- Position must remain FLAT.

## Diagnosis consumed from R16A
```json
{
  "patch_required_before_risk_execution_start": true,
  "risk_has_apparent_xpending_xclaim_fallback": false,
  "risk_uses_xautoclaim": true,
  "safe_to_start_risk_execution_now": false,
  "xautoclaim_known": false,
  "xclaim_known": true,
  "xpending_known": true,
  "xreadgroup_known": true
}
```

## Current Redis command support
```json
{
  "XACK": {
    "known": true,
    "rc": 0,
    "stderr": "",
    "stdout": "xack\n-4\nwrite\nrandom\nfast\n1\n1\n1\n@write\n@stream\n@fast"
  },
  "XAUTOCLAIM": {
    "known": false,
    "rc": 0,
    "stderr": "",
    "stdout": ""
  },
  "XCLAIM": {
    "known": true,
    "rc": 0,
    "stderr": "",
    "stdout": "xclaim\n-6\nwrite\nrandom\nfast\n1\n1\n1\n@write\n@stream\n@fast"
  },
  "XGROUP": {
    "known": true,
    "rc": 0,
    "stderr": "",
    "stdout": "xgroup\n-2\nwrite\ndenyoom\n2\n2\n1\n@write\n@stream\n@slow"
  },
  "XPENDING": {
    "known": true,
    "rc": 0,
    "stderr": "",
    "stdout": "xpending\n-3\nreadonly\nrandom\n1\n1\n1\n@read\n@stream\n@slow"
  },
  "XREADGROUP": {
    "known": true,
    "rc": 0,
    "stderr": "",
    "stdout": "xreadgroup\n-7\nwrite\nmovablekeys\n0\n0\n0\n@write\n@stream\n@slow\n@blocking"
  }
}
```

## Patch design
```json
{
  "do_not_touch": [
    "broker_api.py",
    "execution.py order placement path",
    "strategy action selection",
    "live/broker flags",
    "paper arming flags"
  ],
  "fallback_algorithm_outline": [
    "XPENDING <stream> <group> - + <count> to list pending message ids/consumers/idle times.",
    "Filter rows whose idle_ms >= configured min_idle_ms.",
    "XCLAIM <stream> <group> <consumer> <min_idle_ms> <id...> to claim selected messages.",
    "Process claimed message records through existing decision handling path.",
    "XACK only after successful processing using existing ack semantics.",
    "On ResponseError/unsupported command, publish bounded compatibility error and fail closed."
  ],
  "patch_required": true,
  "primary_target": "app/mme_scalpx/services/risk.py",
  "proof_required_after_patch": [
    "py_compile risk.py and any touched helper files.",
    "AST/static proof that no broker/order placement path was touched.",
    "Import/unit matrix for XAUTOCLAIM-supported path.",
    "Import/unit matrix for XPENDING+XCLAIM fallback path.",
    "Import/unit matrix for unsupported-claim fail-closed path.",
    "No-start safety proof: orders=0, position=FLAT, risk/execution absent, lock:execution absent.",
    "Only after static proof, run a separate no-order runtime arming preflight."
  ],
  "r17_remains_blocked_until": [
    "R16C source patch PASS",
    "R16D static proof PASS",
    "R16E no-start safety proof PASS"
  ],
  "required_behavior": [
    "Detect whether Redis supports XAUTOCLAIM before using it.",
    "If XAUTOCLAIM is supported, preserve the current path.",
    "If XAUTOCLAIM is unavailable but XPENDING and XCLAIM are available, use XPENDING + XCLAIM compatibility fallback for stale pending messages.",
    "If neither safe path is available, fail closed: do not start claim loop, publish bounded health/error once, and prevent arming.",
    "Avoid repeated system:errors spam for unsupported command.",
    "No broker calls, no order writes, no position mutation."
  ],
  "secondary_target": "app/mme_scalpx/core/redisx.py only if the claim helper is centralized there"
}
```

## Source context summary

### app/mme_scalpx/services/risk.py
- exists: `True`
- sha256: `7f2af8402fe59e73372d5b442ffb9cbac04bb3f2a5b7adc7f05c5223560655b9`
- compile_ok: `True`
- hit_count: `14`
- candidate functions:
  - `_batch14_claim_pending` lines 1579-1609
  - `_batch14_process_trade_ledger` lines 1676-1730
  - `_batch14_process_control_commands` lines 1792-1846
  - `_process_trade_ledger` lines 737-762
  - `_process_control_commands` lines 810-835
- first hits:
  - line 738: `        results = RX.xreadgroup(`
  - line 811: `        results = RX.xreadgroup(`
  - line 1579: `def _batch14_claim_pending(self, stream_name: str, now_ns: int, *, count: int = 10):`
  - line 1580: `    claim_fn = getattr(self.redis, "xautoclaim", None)`
  - line 1581: `    if not callable(claim_fn):`
  - line 1586: `        result = claim_fn(`
  - line 1596: `            event="risk_pending_claim_error",`
  - line 1613: `RiskService._claim_pending_entries = _batch14_claim_pending`

### app/mme_scalpx/core/redisx.py
- exists: `True`
- sha256: `64d3102cb83be85aad3977e168a26fbac49b26a2d2c79041f678f2d2be11ef51`
- compile_ok: `True`
- hit_count: `14`
- candidate functions:
  - `_decode_group_info` lines 310-327
  - `xreadgroup` lines 963-1011
  - `axreadgroup` lines 1014-1062
  - `read_envelopes_from_group` lines 1117-1149
  - `aread_envelopes_from_group` lines 1152-1184
- first hits:
  - line 136: `    pending: int`
  - line 323: `        pending=int(info.get("pending", 0)),`
  - line 963: `def xreadgroup(`
  - line 973: `    """Read one or more streams using XREADGROUP."""`
  - line 999: `        raw = redis_client.xreadgroup(`
  - line 1010: `            f"Failed XREADGROUP for {group!r}/{consumer!r}: {exc}"`
  - line 1014: `async def axreadgroup(`
  - line 1024: `    """Read one or more streams using XREADGROUP asynchronously."""`

## Required next approval
```text
I APPROVE A6 CONTROLLED-PAPER RISK CONSUMER COMPATIBILITY SOURCE PATCH ONLY: PATCH RISK CONSUMER XAUTOCLAIM FALLBACK/FAIL-CLOSED PATH ONLY, NO PAPER ORDER, NO REAL LIVE, NO BROKER ORDER, NO REAL MONEY, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT
```