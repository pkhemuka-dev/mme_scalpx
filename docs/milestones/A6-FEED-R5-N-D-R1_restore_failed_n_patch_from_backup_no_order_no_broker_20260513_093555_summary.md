# A6-FEED-R5-N-D-R1 — Restore failed N patch from backup

Generated IST: `2026-05-13T09:35:55.664639+05:30`

## Verdict

`FAIL_A6_FEED_R5_N_D_R1_RESTORE_ATTEMPTED_BUT_VERIFY_FAILED_NO_ORDER`

## Next

`A6-FEED-R5-N-D-R2 manual restore verification / no order`

## Restore

- restore_attempted: `True`
- restore_ok: `True`
- target_after_matches_backup: `True`
- backup_path: `run/_code_backups/A6-FEED-R5-N_fix_option_context_active_ready_field_collision_no_paper_no_broker_order_20260513_093247/feeds.py.before_20260513_093247`

## Compile/import

- before: `{'compile_ok': True, 'compile_error': None, 'import_ok': True, 'import_error': None, 'r5l_helper_present': True}`
- after: `{'compile_ok': False, 'compile_error': 'PyCompileError(\'  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py", line 971\\n    except Exception:\\n    ^^^^^^\\nSyntaxError: invalid syntax\\n\', \'SyntaxError\', SyntaxError(\'invalid syntax\', (\'/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\', 971, 13, \'            except Exception:\\n\', 971, 19)), \'/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feeds.py\')', 'import_ok': True, 'import_error': None, 'r5l_helper_present': True}`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_order_executed: false
- order_sent: false
- paper_start_attempted: false
- real_live_trading_attempted: false
- strategy_threshold_change_attempted: false
