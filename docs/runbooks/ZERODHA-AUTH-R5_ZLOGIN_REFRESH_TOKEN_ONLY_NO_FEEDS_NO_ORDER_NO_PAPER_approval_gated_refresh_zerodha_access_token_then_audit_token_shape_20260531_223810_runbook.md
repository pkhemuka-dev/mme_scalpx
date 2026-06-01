# ZERODHA-AUTH-R5_ZLOGIN_REFRESH_TOKEN_ONLY_NO_FEEDS_NO_ORDER_NO_PAPER

Classification: **PASS_ZERODHA_AUTH_R5_ZLOGIN_TOKEN_REFRESH_ONLY_NO_FEEDS_NO_ORDER_NO_PAPER**

## Scope

Approval-gated Zerodha login/token refresh only.

No feeds start, no risk, no execution, no orders, no paper/live.

## Checks

- zlogin_exit=0
- safety_preflight_ok=1
- safety_ok=1
- api_has_key=1
- token_has_access=1

## Artifacts

- zlogin log: `run/logs/ZERODHA-AUTH-R5_ZLOGIN_REFRESH_TOKEN_ONLY_NO_FEEDS_NO_ORDER_NO_PAPER_approval_gated_refresh_zerodha_access_token_then_audit_token_shape_20260531_223810_zlogin.log`
- token audit: `run/audits/ZERODHA-AUTH-R5_ZLOGIN_REFRESH_TOKEN_ONLY_NO_FEEDS_NO_ORDER_NO_PAPER_approval_gated_refresh_zerodha_access_token_then_audit_token_shape_20260531_223810_token_shape_after_zlogin.json`
- state: `run/audits/ZERODHA-AUTH-R5_ZLOGIN_REFRESH_TOKEN_ONLY_NO_FEEDS_NO_ORDER_NO_PAPER_approval_gated_refresh_zerodha_access_token_then_audit_token_shape_20260531_223810_state.txt`

## Safety

- orders_before=0
- orders_after=0
- risk_stream_after=0
- execution_stream_after=0
- feeds_proc_after=0
- risk_proc_after=0
- execution_proc_after=0
