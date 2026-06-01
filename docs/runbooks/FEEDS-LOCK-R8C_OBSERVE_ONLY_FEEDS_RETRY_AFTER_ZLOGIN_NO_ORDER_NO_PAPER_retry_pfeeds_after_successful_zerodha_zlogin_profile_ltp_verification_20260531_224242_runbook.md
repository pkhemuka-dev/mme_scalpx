# FEEDS-LOCK-R8C_OBSERVE_ONLY_FEEDS_RETRY_AFTER_ZLOGIN_NO_ORDER_NO_PAPER

Classification: **PASS_FEEDS_LOCK_R8C_OBSERVE_ONLY_FEEDS_RETRY_AFTER_ZLOGIN_NO_ORDER_NO_PAPER**

## Scope

Observe-only feeds retry after successful Zerodha zlogin verification.

## Checks

- patch_ok=1
- compile_ok=1
- zlogin_proof_ok=1
- safety_preflight_ok=1
- orders_ok=1
- risk_execution_ok=1
- feeds_started_ok=1
- feeds_lock_ok=1
- stream_growth_ok=1

## Safety

- No risk service
- No execution service
- No orders
- No paper/live enablement

## State

- observe_file: `run/audits/FEEDS-LOCK-R8C_OBSERVE_ONLY_FEEDS_RETRY_AFTER_ZLOGIN_NO_ORDER_NO_PAPER_retry_pfeeds_after_successful_zerodha_zlogin_profile_ltp_verification_20260531_224242_observe_window.txt`
- lock_feeds_type=string
- lock_feeds_pttl=27265
- lock_feeds_value=feeds:mme-scalpx:17336

## Safety counters

- orders_before=0
- orders_after=0
- risk_stream_after=0
- execution_stream_after=0
- risk_proc_after=0
- execution_proc_after=0
