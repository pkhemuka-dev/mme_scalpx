# B1-PROFIT-LIVE-R39WK_DYNAMIC_FIELD_DERIVATION_PATCH_NO_START_NO_ORDER_additive_features_surface_dynamic_fields_from_existing_live_snapshot_history_no_threshold_change_20260603_152256 runbook

Additive dynamic-field derivation patch in features.py.

No start.
No stop.
No Redis delete.
No lock delete.
No paper.
No broker order.
No threshold change.
No candidate forcing.

Rollback:
```bash
cp -a "run/_code_backups/B1-PROFIT-LIVE-R39WK_DYNAMIC_FIELD_DERIVATION_PATCH_NO_START_NO_ORDER_additive_features_surface_dynamic_fields_from_existing_live_snapshot_history_no_threshold_change_20260603_152256/features.py.before_r39wk" "app/mme_scalpx/services/features.py"
.venv/bin/python -m py_compile "app/mme_scalpx/services/features.py"
```
