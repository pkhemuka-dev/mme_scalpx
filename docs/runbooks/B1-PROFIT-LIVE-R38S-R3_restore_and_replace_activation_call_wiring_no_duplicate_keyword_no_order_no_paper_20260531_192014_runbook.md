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
