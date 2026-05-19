# A6-FEED-R5-N — Fix option-context active ready field collision

Generated IST: `2026-05-13T09:32:47.476106+05:30`

## Verdict

`FAIL_A6_FEED_R5_N_PATCH_COMPILE_IMPORT_FAILED_NO_ORDER`

## Next

`A6-FEED-R5-N-D source patch failure diagnostic / restore from backup if needed`

## Patch

- target: `app/mme_scalpx/services/feeds.py`
- source_patch_applied: `True`
- patch_result: `{'ok': True, 'reason': 'patched', 'patched': True, 'backup_path': 'run/_code_backups/A6-FEED-R5-N_fix_option_context_active_ready_field_collision_no_paper_no_broker_order_20260513_093247/feeds.py.before_20260513_093247', 'backup_sha256': '21be2ce47280e6c23f43421cbc374bb3ab47472440742ccb7cd9ed225616057c', 'diff_path': 'run/audits/A6-FEED-R5-N_fix_option_context_active_ready_field_collision_no_paper_no_broker_order_20260513_093247_feeds_py_unified_diff.patch', 'diff_sha256': '8a23d0ec5309a8571e9653bf7dfaa78dacda9ca5ef6d379f655e88d3a0f723d3', 'target_sha256_before': '21be2ce47280e6c23f43421cbc374bb3ab47472440742ccb7cd9ed225616057c', 'target_sha256_after': 'd33d3af99827cfeda3f38f088408ddda8a9daa5a6626312beda3504fec232812', 'context_fields_assignment_match_count': 1}`
- compile_import: `{'compile_ok': False, 'compile_error': 'PyCompileError(\'  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py", line 971\\n    except Exception:\\n    ^^^^^^\\nSyntaxError: invalid syntax\\n\', \'SyntaxError\', SyntaxError(\'invalid syntax\', (\'/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\', 971, 13, \'            except Exception:\\n\', 971, 19)), \'/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\')', 'import_ok': False, 'import_error': "SyntaxError('invalid syntax', ('/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py', 971, 13, '            except Exception:\\n', 971, 19))", 'r5l_helper_present': False}`

## Collision

- option_context_ready_before: `selected_put_iv`
- option_context_ready_after: `selected_put_iv`
- expected: `1`

## Hash readiness

- before: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': False, 'state:dhan_context:mme': True}`
- after: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': False, 'state:dhan_context:mme': True}`
- missing_after: `{'state:provider_runtime:mme': [], 'state:feed:futures:active': [], 'state:feed:selected_option:active': [], 'state:feed:option_context:active': ['ready'], 'state:dhan_context:mme': []}`

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
