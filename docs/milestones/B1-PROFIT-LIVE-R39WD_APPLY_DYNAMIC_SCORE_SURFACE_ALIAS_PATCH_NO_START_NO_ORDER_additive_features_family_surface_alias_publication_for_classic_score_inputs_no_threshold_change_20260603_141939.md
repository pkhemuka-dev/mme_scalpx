# B1-PROFIT-LIVE-R39WD_APPLY_DYNAMIC_SCORE_SURFACE_ALIAS_PATCH_NO_START_NO_ORDER_additive_features_family_surface_alias_publication_for_classic_score_inputs_no_threshold_change_20260603_141939

Classification: `BLOCKED_R39WD_PATCH_PROOF_FAILED`

## What changed
- Added an additive helper in `features.py` to publish dynamic score alias keys consumed by classic family leaves.
- Inserted the helper before `family_frames_json` publication sites.
- No strategy thresholds changed.
- No candidate forcing.
- No paper/live/order enablement.

## Proof
- marker_ok: True
- helper_ok: True
- call_count: 6
- compile_ok: False
- forbidden_flags: {'paper_flag_enabled': False, 'broker_order_enabled': False}

## Backup
- `run/_code_backups/B1-PROFIT-LIVE-R39WD_APPLY_DYNAMIC_SCORE_SURFACE_ALIAS_PATCH_NO_START_NO_ORDER_additive_features_family_surface_alias_publication_for_classic_score_inputs_no_threshold_change_20260603_141939/features.py.before_r39wd`

## Next route
- Do not paper.
- If market is still live and you want to validate runtime behavior, restart observe-only stack only through existing safe pauto/pstack route.
- Then rerun R39WA to confirm score/regime surfaces now move.