# A6-FEED-R3C-R4_after_market_zerodha_auth_session_bootstrap_failure_diagnostic_no_start_no_order_no_broker_order_20260513_080309

## Purpose
After-market diagnostic for pfeeds startup failure after R5G-R2.

## Current blocker
Zerodha bootstrap quote failed before feeds could start:
`kite.ltp('NSE:NIFTY 50') failed: Incorrect api_key or access_token`.

## Safety
- source_patch_applied: false
- operator_helper_patch_applied: false
- redis_hash_write_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Next
A6-FEED-R3C-R5-AUTH-RUNBOOK if classified.
