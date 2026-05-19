# A6-FEED-R3C-R4_after_market_zerodha_auth_session_bootstrap_failure_diagnostic_no_start_no_order_no_broker_order_20260513_080309 runbook

Next:
A6-FEED-R3C-R5-AUTH-RUNBOOK

Tomorrow before market:
1. Refresh Zerodha login/session.
2. Run auth/token smoke check.
3. Run A6-FEED-R3C-R3 feed recovery.
4. If feeds recover, run A6-FEED-R5G-R3 or A6-FEED-R5 as indicated.
5. Only after A6-FEED-R5 PASS can A6-PAPER watcher rerun.

Still forbidden:
- no paper/live enablement
- no broker order
- no risk/execution start
- no threshold relaxation
