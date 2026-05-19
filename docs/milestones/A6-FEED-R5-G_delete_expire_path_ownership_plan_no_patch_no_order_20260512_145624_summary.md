# A6-FEED-R5-G — Delete/expire path ownership plan

Generated IST: `2026-05-12T14:56:24.722125+05:30`

## Verdict

`PASS_A6_FEED_R5_G_DELETE_EXPIRE_OWNERSHIP_PLAN_READY_NO_PATCH_NO_ORDER`

## Root cause

`DELETE_EXPIRE_HITS_ARE_LIKELY_GENERIC_FALSE_POSITIVES_BUT_DURABLE_OWNER_STILL_UNPROVEN`

## Patch plan type

`DURABLE_OWNER_AUDIT_OR_PATCH_PLAN_AFTER_APPROVAL`

## Classification inputs

`{'all_required_absent_now': False, 'direct_delete_path_file_count': 0, 'direct_write_path_file_count': 0, 'generic_delete_path_file_count': 5, 'generic_write_path_file_count': 9, 'exact_key_reference_file_count': 1, 'dependency_ok': True}`

## Direct delete paths

`{k: len(v) for k, v in direct_delete_paths.items()}`

## Direct write paths

`{k: len(v) for k, v in direct_write_paths.items()}`

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

`A6-FEED-R5-H durable owner final patch plan / no patch until approved`
