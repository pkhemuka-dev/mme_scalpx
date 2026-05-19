# A6-FEED-R5D_approved_minimal_features_provider_mapping_patch_no_order_no_broker_no_threshold_change_20260513_073613

## Purpose
Approved minimal features.py source patch for A6-FEED provider mapping.

## Patch
Separate classic provider readiness from MISO/Dhan option-context readiness:
- classic provider path can be consumer-valid when futures + selected-option providers are healthy and surfaces are present
- MISO remains fail-closed while Dhan option context is degraded/stale/unsynced
- raw snapshot sync truth remains preserved via snapshot_sync_valid and snapshot validity
- no strategy thresholds changed
- no forced candidates
- no paper/live enablement

## Safety
- source_patch_applied: true
- operator_helper_patch_applied: false
- redis_hash_write_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- broker_order_calls_executed: false
- order_sent: false
- risk_execution_start_attempted: false

## Verdict
See proof: run/proofs/A6-FEED-R5D_approved_minimal_features_provider_mapping_patch_no_order_no_broker_no_threshold_change_20260513_073613.txt

## Next
A6-FEED-R5E compile/static/source proof, then live A6-FEED-R5 after service reload during market session.
