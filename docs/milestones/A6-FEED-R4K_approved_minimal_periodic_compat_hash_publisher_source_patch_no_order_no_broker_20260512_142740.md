# A6-FEED-R4K_approved_minimal_periodic_compat_hash_publisher_source_patch_no_order_no_broker_20260512_142740

## Purpose
Approved minimal source patch for periodic A6-FEED compatibility hash publication inside feeds.

## Patch
 now periodically clones durable source hashes to A6 compatibility hashes while the feeds service owns live source publication.

## Safety
- redis_hash_write_attempted: false by patch command
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Verdict
See proof: run/proofs/A6-FEED-R4K_approved_minimal_periodic_compat_hash_publisher_source_patch_no_order_no_broker_20260512_142740.txt

## Next
A6-FEED-R4L restart observe-only feeds and prove compatibility hashes are durable.
