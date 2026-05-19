# A6-FEED-R5-N-R5 — Exact option-context HSET ready overwrite fix

Generated IST: `2026-05-13T10:23:14.174361+05:30`

## Verdict
`BLOCKED_A6_FEED_R5_N_R5_PATCH_APPLIED_BUT_READY_PROOF_FAILED_NO_ORDER`

## Next
`A6-FEED-R5-N-R5D post-patch readiness diagnostic / no patch / no order`

## Readiness
- option_context.ready before: `selected_put_iv`
- option_context.ready after: `selected_put_iv`
- dhan_context.ready after: `None`

## Patch
- source_patch_applied: `True`
- patch_result: `{'ok': True, 'reason': 'patched', 'patched': True, 'old_count': 1, 'already_count': 0, 'tmp_path': '/tmp/a6_r5n_r5_lxkmwli5/feeds.py', 'tmp_compile': {'compile_ok': True, 'compile_error': None}, 'backup_path': 'run/_code_backups/A6-FEED-R5-N-R5_exact_option_context_hset_ready_overwrite_fix_no_paper_no_broker_order_20260513_102302/feeds.py.before_20260513_102302', 'backup_sha256': '9d4d23e8b0d3583c0a71e3dae1f84aea99e391c2567589b2c40fc341411f2131', 'before_replace': 'run/_code_backups/A6-FEED-R5-N-R5_exact_option_context_hset_ready_overwrite_fix_no_paper_no_broker_order_20260513_102302/feeds.py.before_replace_20260513_102302', 'diff_path': 'run/audits/A6-FEED-R5-N-R5_exact_option_context_hset_ready_overwrite_fix_no_paper_no_broker_order_20260513_102302_feeds_py_diff.patch', 'diff_sha256': '3a354c2ec8a0b613d194ff74a4a013509b49980d736885691ae064bfd840aaca', 'target_sha256_after': '71517a3c9f118b642eec1695b2761f947f0afc5206da86efcd5d4c6aec914007'}`

## Safety
- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false
- paper_start_attempted: false
- real_live_trading_attempted: false
