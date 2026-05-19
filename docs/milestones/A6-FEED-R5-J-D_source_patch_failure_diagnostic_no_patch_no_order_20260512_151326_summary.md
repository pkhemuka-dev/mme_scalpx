# A6-FEED-R5-J-D — Source patch failure diagnostic

Generated IST: `2026-05-12T15:13:26.345133+05:30`

## Verdict

`PASS_A6_FEED_R5_J_D_SOURCE_PATCH_FAILURE_CLASSIFIED_NO_PATCH_NO_ORDER`

## Root cause

`ORIGINAL_PATCH_SEARCHED_ONLY_DIRECT_XADD_BUT_FEEDS_PY_HAS_NON_XADD_PUBLISH_SEAMS`

## Restore analysis

`{'backup_path': 'run/_code_backups/A6-FEED-R5-J_source_patch_minimal_durable_canonical_provider_feed_hash_owner_no_paper_no_live_no_broker_order_20260512_150847/feeds.py.before_20260512_150847', 'backup_exists': True, 'backup_sha256': '76f9116b1d5815c7311436ac2f8e474475e647c1a509cf8f006376ae441c16be', 'target_sha256': '76f9116b1d5815c7311436ac2f8e474475e647c1a509cf8f006376ae441c16be', 'restore_needed': False, 'patch_marker_present': False}`

## Classification inputs

`{'dependency_ok': True, 'safety_ok': True, 'compile_ok': True, 'parse_ok': True, 'restore_needed': False, 'literal_xadd_count': 6, 'redis_call_inventory_count': 71, 'candidate_hook_seam_count': 60, 'provider_blocker_count': 30}`

## Safety

- source_patch_applied: false
- restore_attempted: false
- service_start_attempted: false
- service_stop_attempted: false
- hash_publish_attempted: false
- broker_order_executed: false
- order_sent: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R5-K corrected seam patch plan / no patch until approved`
