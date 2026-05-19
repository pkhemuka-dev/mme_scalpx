# A6-FEED-R3C-R4E-R3-SYNTAX-REPAIR_repair_orphan_except_after_bad_quote_quarantine_patch_no_model_change_no_order_no_broker_20260513_093343

## Purpose
Repair syntax break introduced during A6-FEED-R3C-R4E-R2 bad-quote quarantine patch.

## Repair
- Removed orphan `except Exception:` block after `return None, None`
- Preserved no-swap/no-clamp inverted bid/ask quarantine
- Updated normalize_tick type contract to allow `None, None`
- Preserved app/mme_scalpx/core/models.py unchanged

## Safety
- source_patch_applied: true
- redis_hash_write_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Verdict
See proof: run/proofs/A6-FEED-R3C-R4E-R3-SYNTAX-REPAIR_repair_orphan_except_after_bad_quote_quarantine_patch_no_model_change_no_order_no_broker_20260513_093343.txt
