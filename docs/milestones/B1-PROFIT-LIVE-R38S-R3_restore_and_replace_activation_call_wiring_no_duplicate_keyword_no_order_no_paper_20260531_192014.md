# B1-PROFIT-LIVE-R38S-R3_restore_and_replace_activation_call_wiring_no_duplicate_keyword_no_order_no_paper_20260531_192014

## Verdict
`PASS_R38S_R3_RESTORE_REPLACE_WIRING_STATIC_SMOKE_NO_ORDER`

## What changed
- Restored from R38S-R2 pre-patch backup.
- Replaced the existing activation call pair instead of adding a duplicate keyword.
- Patched only `app/mme_scalpx/services/strategy.py`.
- `live_orders_allowed` remains blocked.

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``
- pauto_stopped: `True`
- pseal_pass: `True`
- no_live_processes: `True`

## Smoke
- smoke_pass: `True`
- activation call count one: `True`
- allow candidate promotion call count one: `True`
- old allow candidate promotion removed: `True`
- MISO ack blocks: `True`
- broker/live env blocks: `True`
- risk unchanged this batch: `True`
- execution unchanged this batch: `True`

## Rule
No paper/risk/execution/order was started.


# B1-PROFIT-LIVE-R38S-R3_restore_and_replace_activation_call_wiring_no_duplicate_keyword_no_order_no_paper_20260531_192014 runbook

## Rollback
cp run/_code_backups/B1-PROFIT-LIVE-R38S-R2_repair_activation_call_wiring_static_smoke_no_order_no_paper_20260531_191853_strategy.py.backup app/mme_scalpx/services/strategy.py
.venv/bin/python -m py_compile app/mme_scalpx/services/strategy.py

## Next
R38T:
- synthetic eligible-classic report-only bridge smoke
- prove safe_to_promote appears only under explicit classic 1-lot paper-only env/scope
- prove live_orders_allowed remains false
- no risk start
- no execution start
- no order
