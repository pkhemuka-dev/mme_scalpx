# A6-FEED-R3C-R4E-R5-FRESH-PATCH_fresh_apply_bad_quote_quarantine_current_source_no_model_change_no_order_no_broker_20260513_101624

## Purpose
Fresh current-source patch for inverted bid/ask quarantine after R4F-R2 proved the guard was missing.

## Patch
- app/mme_scalpx/services/feeds.py only
- app/mme_scalpx/core/models.py unchanged
- malformed inverted bid/ask quote returns None, None before FeedTick construction
- handle_raw_tick safely rejects tick is None
- no bid/ask swap or clamp
- no service start/stop
- no broker/order/risk/execution

## Verdict
See proof: run/proofs/A6-FEED-R3C-R4E-R5-FRESH-PATCH_fresh_apply_bad_quote_quarantine_current_source_no_model_change_no_order_no_broker_20260513_101624.txt
