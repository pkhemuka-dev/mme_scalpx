# A6-FEED-R3C-R4E-R4-SYNTAX-REPAIR_direct_remove_orphan_except_after_return_no_model_change_no_order_no_broker_20260513_093715

## Purpose
Direct syntax repair after R4F proved orphan except still present.

## Repair
- Removed orphan `except Exception:` block after `return None, None`
- Preserved bad quote quarantine
- Preserved models.py unchanged
- No service start/stop
- No broker/order/risk/execution

## Verdict
See proof: run/proofs/A6-FEED-R3C-R4E-R4-SYNTAX-REPAIR_direct_remove_orphan_except_after_return_no_model_change_no_order_no_broker_20260513_093715.txt
