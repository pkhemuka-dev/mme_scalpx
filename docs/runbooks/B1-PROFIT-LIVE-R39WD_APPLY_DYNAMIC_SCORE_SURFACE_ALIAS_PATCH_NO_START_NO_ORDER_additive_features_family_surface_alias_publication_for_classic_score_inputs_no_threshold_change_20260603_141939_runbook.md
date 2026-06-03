# B1-PROFIT-LIVE-R39WD_APPLY_DYNAMIC_SCORE_SURFACE_ALIAS_PATCH_NO_START_NO_ORDER_additive_features_family_surface_alias_publication_for_classic_score_inputs_no_threshold_change_20260603_141939 runbook

Applied narrow additive dynamic score alias publication patch in features.py only.

No service start.
No service stop.
No Redis delete.
No lock delete.
No paper.
No broker order.
No threshold change.

Rollback:
```bash
cp -a "run/_code_backups/B1-PROFIT-LIVE-R39WD_APPLY_DYNAMIC_SCORE_SURFACE_ALIAS_PATCH_NO_START_NO_ORDER_additive_features_family_surface_alias_publication_for_classic_score_inputs_no_threshold_change_20260603_141939/features.py.before_r39wd" "app/mme_scalpx/services/features.py"
.venv/bin/python -m py_compile "app/mme_scalpx/services/features.py"
```
