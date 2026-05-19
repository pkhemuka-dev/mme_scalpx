# A6-FEED-R5-J — Source patch minimal durable canonical provider/feed hash owner

Generated IST: `2026-05-12T15:08:47.583500+05:30`

## Verdict

`FAIL_A6_FEED_R5_J_PATCH_COMPILE_IMPORT_FAILED_NO_ORDER`

## Patch

- target: `app/mme_scalpx/services/feeds.py`
- source_patch_applied: `False`
- patch_result: `{'ok': False, 'reason': 'no_xadd_hook_seam_found_in_feeds_py', 'patched': False, 'backup_path': 'run/_code_backups/A6-FEED-R5-J_source_patch_minimal_durable_canonical_provider_feed_hash_owner_no_paper_no_live_no_broker_order_20260512_150847/feeds.py.before_20260512_150847', 'backup_sha256': '76f9116b1d5815c7311436ac2f8e474475e647c1a509cf8f006376ae441c16be'}`
- compile_ok: `True`
- import_ok: `True`
- helper_present: `False`

## Hash readiness

- before present: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': True, 'state:dhan_context:mme': False}`
- before ready: `{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`
- after present: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': True, 'state:dhan_context:mme': False}`
- after ready: `{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`

## Consumer blocker count

- before: `48`
- after: `48`

## Safety

- service_start_attempted: false
- service_stop_attempted: false
- risk_execution_start_attempted: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- broker_order_executed: false
- order_sent: false
- strategy_threshold_change_attempted: false
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`

## Next

`A6-FEED-R5-J-D source patch failure diagnostic / restore from backup if needed`
