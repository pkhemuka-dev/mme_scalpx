# B1-PROFIT-LIVE-R39WE_AST_SAFE_DYNAMIC_SCORE_ALIAS_PATCH_NO_START_NO_ORDER_apply_ast_statement_level_features_family_score_alias_patch_with_auto_rollback_on_compile_fail_20260603_142906 runbook

AST-safe dynamic score alias patch.

No start.
No stop.
No Redis delete.
No lock delete.
No paper.
No broker order.
No threshold change.

Rollback:
```bash
cp -a "run/_code_backups/B1-PROFIT-LIVE-R39WE_AST_SAFE_DYNAMIC_SCORE_ALIAS_PATCH_NO_START_NO_ORDER_apply_ast_statement_level_features_family_score_alias_patch_with_auto_rollback_on_compile_fail_20260603_142906/features.py.before_r39we" "app/mme_scalpx/services/features.py"
.venv/bin/python -m py_compile "app/mme_scalpx/services/features.py"
```
