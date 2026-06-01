# B1-PROFIT-LIVE-R38R_tiny_classic_controlled_paper_activation_bridge_patch_fixture_no_order_no_paper_20260531_191253 runbook

## Rollback
cp run/_code_backups/B1-PROFIT-LIVE-R38R_tiny_classic_controlled_paper_activation_bridge_patch_fixture_no_order_no_paper_20260531_191253_strategy.py.backup app/mme_scalpx/services/strategy.py
.venv/bin/python -m py_compile app/mme_scalpx/services/strategy.py

## Next batch
R38S:
- static source audit
- activation report smoke fixture
- prove no live_orders_allowed
- prove top-level order intent remains disabled
- no risk/execution/order
