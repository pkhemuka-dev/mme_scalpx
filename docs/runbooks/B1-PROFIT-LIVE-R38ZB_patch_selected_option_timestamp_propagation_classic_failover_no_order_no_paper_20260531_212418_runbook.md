# B1-PROFIT-LIVE-R38ZB_patch_selected_option_timestamp_propagation_classic_failover_no_order_no_paper_20260531_212418 runbook

## Rollback
cp run/_code_backups/B1-PROFIT-LIVE-R38ZB_patch_selected_option_timestamp_propagation_classic_failover_no_order_no_paper_20260531_212418_features.py.backup app/mme_scalpx/services/features.py
.venv/bin/python -m py_compile app/mme_scalpx/services/features.py

## Next
R38ZC:
- offline projection on sealed records
- verify whether timestamp propagation would make feature view structurally valid when selected-option timestamps exist
- no risk/execution/order
