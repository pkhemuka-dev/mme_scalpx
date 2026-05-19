# A6-FEED-R5-L — Live corrected seam source patch

Generated IST: `2026-05-13T09:23:05.039755+05:30`

## Verdict

`BLOCKED_A6_FEED_R5_L_PATCH_APPLIED_BUT_HASH_OR_PERSISTENCE_FAILED_NO_ORDER`

## Next

`A6-FEED-R5-L-D patch/hash persistence diagnostic / no broker order`

## Patch

- source_patch_applied: `True`
- patch_result: `{'ok': True, 'reason': 'patched', 'patched': True, 'seam': {'ok': True, 'function': '_publish_dhan_context_event', 'call_line': 1914, 'insert_after_line': 1918}, 'backup_path': 'run/_code_backups/A6-FEED-R5-L_live_corrected_seam_source_patch_no_paper_no_broker_order_20260513_092305/feeds.py.before_20260513_092305', 'backup_sha256': '76f9116b1d5815c7311436ac2f8e474475e647c1a509cf8f006376ae441c16be', 'diff_path': 'run/audits/A6-FEED-R5-L_live_corrected_seam_source_patch_no_paper_no_broker_order_20260513_092305_feeds_py_unified_diff.patch', 'diff_sha256': 'e8decaabd6aed0b9fa9c786acad7dd1cc182d83f434f50c26934d102b5e88a82', 'target_sha256_before': '76f9116b1d5815c7311436ac2f8e474475e647c1a509cf8f006376ae441c16be', 'target_sha256_after': '8f992548835ffda8a2ef37207ddfc1ffd157b62c5d68146ddce6b1247f61413d'}`
- compile_import: `{'compile_ok': True, 'compile_error': None, 'import_ok': True, 'import_error': None, 'helper_present': True}`

## Hash readiness

- before present: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': True, 'state:dhan_context:mme': False}`
- before ready: `{'state:provider_runtime:mme': False, 'state:feed:futures:active': False, 'state:feed:selected_option:active': False, 'state:feed:option_context:active': False, 'state:dhan_context:mme': False}`
- after present: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': True, 'state:dhan_context:mme': True}`
- after ready: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': False, 'state:dhan_context:mme': True}`

## Consumer blockers

- before: `54`
- after: `54`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- strategy_threshold_change_attempted: false
