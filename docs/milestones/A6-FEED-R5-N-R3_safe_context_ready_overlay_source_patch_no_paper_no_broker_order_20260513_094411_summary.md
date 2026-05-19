# A6-FEED-R5-N-R3 — Safe context-ready overlay source patch

Generated IST: `2026-05-13T09:44:11.020304+05:30`

## Verdict

`BLOCKED_A6_FEED_R5_N_R3_PATCH_APPLIED_BUT_READY_PROOF_FAILED_NO_ORDER`

## Next

`A6-FEED-R5-N-R3D post-patch readiness diagnostic / no patch / no order`

## Patch

- source_patch_applied: `True`
- patch_result: `{'ok': True, 'reason': 'patched', 'patched': True, 'anchor': {'ok': True, 'helper_line': 2985, 'helper_end': 3058, 'anchor': {'line': 3045, 'end_line': 3045, 'text': 'context_fields = _a6_r5l_feed_hash_fields(context, "dhan", "option_context_active")', 'context': [{'line': 3041, 'text': '        _a6_r5l_feed_hash_fields(selected, selected.get("provider") or "", "selected_option_active"),'}, {'line': 3042, 'text': '    )'}, {'line': 3043, 'text': ''}, {'line': 3044, 'text': '    if context:'}, {'line': 3045, 'text': '        context_fields = _a6_r5l_feed_hash_fields(context, "dhan", "option_context_active")'}, {'line': 3046, 'text': '        results["state:feed:option_context:active"] = _a6_r5l_hset_mapping(redis_client, "state:feed:option_context:active", context_fields)'}, {'line': 3047, 'text': '        results["state:dhan_context:mme"] = _a6_r5l_hset_mapping(redis_client, "state:dhan_context:mme", dict(context_fields, kind="dhan_context_active"))'}, {'line': 3048, 'text': '    else:'}, {'line': 3049, 'text': '        results["state:feed:option_context:active"] = {"key": "state:feed:option_context:active", "ok": False, "reason": "dhan_option_context_stream_absent"}'}]}}, 'backup_path': 'run/_code_backups/A6-FEED-R5-N-R3_safe_context_ready_overlay_source_patch_no_paper_no_broker_order_20260513_094411/feeds.py.before_20260513_094411', 'backup_sha256': '8f992548835ffda8a2ef37207ddfc1ffd157b62c5d68146ddce6b1247f61413d', 'failed_current_copy': 'run/_code_backups/A6-FEED-R5-N-R3_safe_context_ready_overlay_source_patch_no_paper_no_broker_order_20260513_094411/feeds.py.before_replace_20260513_094411', 'tmp_candidate_path': '/tmp/a6_feed_r5n_r3_6vthvqoz/feeds.py', 'tmp_candidate_compile': {'compile_ok': True, 'compile_error': None}, 'diff_path': 'run/audits/A6-FEED-R5-N-R3_safe_context_ready_overlay_source_patch_no_paper_no_broker_order_20260513_094411_feeds_py_unified_diff.patch', 'diff_sha256': 'aeaee409aee7ea5263cc46c150f2b41f7ad117fb6e99b8b2afd2cce68db10dfc', 'target_sha256_before': '8f992548835ffda8a2ef37207ddfc1ffd157b62c5d68146ddce6b1247f61413d', 'target_sha256_after': 'd177050d1e3b705ff09e27c63e2ce5c39cada2c531556cd9cc7d3aacedd50e4f'}`

## Compile/import

- before: `{'compile_ok': True, 'compile_error': None, 'import_ok': True, 'import_error': None, 'r5l_helper_present': True}`
- after: `{'compile_ok': True, 'compile_error': None, 'import_ok': True, 'import_error': None, 'r5l_helper_present': True}`

## Hash readiness

- option_context_ready_before: `selected_put_iv`
- option_context_ready_after: `selected_put_iv`
- dhan_context_ready_after: `1`
- ready_after: `{'state:provider_runtime:mme': True, 'state:feed:futures:active': True, 'state:feed:selected_option:active': True, 'state:feed:option_context:active': False, 'state:dhan_context:mme': True}`
- missing_after: `{'state:provider_runtime:mme': [], 'state:feed:futures:active': [], 'state:feed:selected_option:active': [], 'state:feed:option_context:active': ['ready'], 'state:dhan_context:mme': []}`

## Consumer blockers

- before: `60`
- after: `60`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- strategy_threshold_change_attempted: false
