# A6-FEED-R5-E — Canonical hash persistence/keyspace diagnostic

Generated IST: `2026-05-12T14:26:09.571489+05:30`

## Verdict

`PASS_A6_FEED_R5_E_CANONICAL_HASH_PERSISTENCE_KEYSPACE_CLASSIFIED_NO_PATCH_NO_ORDER`

## Root cause

`CANONICAL_HASHES_REMOVED_AFTER_R4H_R2_WITHOUT_CURRENT_DB_PRESENCE`

## Classification inputs

`{'all_required_absent_all_dbs': True, 'required_found_nonzero_db': False, 'alt_keys_present_db0': True, 'dependency_ok': True}`

## Required hashes found in any DB

`{'state:provider_runtime:mme': [], 'state:feed:futures:active': [], 'state:feed:selected_option:active': [], 'state:feed:option_context:active': [], 'state:dhan_context:mme': []}`

## Alt keys by DB

`{0: True, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False, 13: False, 14: False, 15: False}`

## Safety

- source_patch_applied: false
- service_start_attempted: false
- service_stop_attempted: false
- hash_publish_attempted: false
- broker_order_executed: false
- order_sent: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R5-F hash removal writer/owner audit / no patch / no order`
