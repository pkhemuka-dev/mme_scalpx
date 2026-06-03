# B1-PROFIT-LIVE-R39WD_R1_ROLLBACK_FAILED_DYNAMIC_SCORE_PATCH_NO_START_NO_ORDER_20260603_142347

Classification: `PASS_R39WD_R1_ROLLBACK_COMPLETE_FEATURES_COMPILE_OK_NO_START_NO_ORDER`

## Action
- Rolled back failed R39WD features.py patch from backup.
- Preserved failed patched file for forensic inspection.
- No service start/stop.
- No Redis delete.
- No paper/live/order.

## Proof
- compile_ok: True
- r39wd_marker_present_after_rollback: False
- restored_from_backup: `run/_code_backups/B1-PROFIT-LIVE-R39WD_APPLY_DYNAMIC_SCORE_SURFACE_ALIAS_PATCH_NO_START_NO_ORDER_additive_features_family_surface_alias_publication_for_classic_score_inputs_no_threshold_change_20260603_141939/features.py.before_r39wd`
- failed_patch_preserved: `run/_code_backups/B1-PROFIT-LIVE-R39WD_R1_ROLLBACK_FAILED_DYNAMIC_SCORE_PATCH_NO_START_NO_ORDER_20260603_142347/features.py.failed_r39wd_syntax_error`

## Next route
- Do not restart until rollback PASS is confirmed.
- Next patch must insert helper call outside dictionary literals, ideally immediately after family_frames is fully constructed, not before the `family_frames_json` dict key.