# R38DK-R1 Patch Note

Tag: LANE-X-R38DK_R1_CORRECTED_MISC_COMPRESSION_DIAG_ENV_PATCH_NO_RESTART_NO_ARM_NO_ORDER_20260617_125027
Created: 2026-06-17T12:50:28+05:30

Patched:
- app/mme_scalpx/services/feature_family/misc_surface.py

Backup:
- app/mme_scalpx/services/feature_family/misc_surface.py.r38dk_r1_backup_20260617_125027

Patch type:
- Guarded diagnostic/config patch.
- Default behavior unchanged unless explicit env vars are set later.
- No candidate forcing.
- No risk/execution/order path touched.
- No restart performed.

Adds live MISC compression diagnostics:
- compression_width_min_threshold
- compression_width_max_threshold
- compression_min_count_threshold
- compression_width_below_min
- compression_width_above_max
- compression_count_below_min
- compression_width_env_override_active
- compression_width_original_min_threshold
- compression_width_original_max_threshold
- compression_original_min_count_threshold

Optional future env hooks, not set by this patch:
- SCALPX_MISC_COMPRESSION_WIDTH_MIN_PCT
- SCALPX_MISC_COMPRESSION_WIDTH_MAX_PCT
- SCALPX_MISC_COMPRESSION_MIN_COUNT

Safety:
- before streams: 0/0/0/0
- after streams: 0/0/0/0
- compile_rc: 0
