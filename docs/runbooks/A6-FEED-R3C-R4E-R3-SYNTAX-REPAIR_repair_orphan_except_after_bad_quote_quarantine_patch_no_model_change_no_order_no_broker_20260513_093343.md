# A6-FEED-R3C-R4E-R3-SYNTAX-REPAIR_repair_orphan_except_after_bad_quote_quarantine_patch_no_model_change_no_order_no_broker_20260513_093343 runbook

Next batch:
A6-FEED-R3C-R4F

A6-FEED-R3C-R4F must prove:
- feeds.py compiles
- no orphan except remains
- models.py unchanged
- bad quote quarantine exists
- handler safely accepts tick is None
- no broker/order/risk/execution/paper/live surfaces

After R4F:
A6-FEED-R3C-R3-LIVE-OPEN-R3 feed proof during live market after feed service reload.
