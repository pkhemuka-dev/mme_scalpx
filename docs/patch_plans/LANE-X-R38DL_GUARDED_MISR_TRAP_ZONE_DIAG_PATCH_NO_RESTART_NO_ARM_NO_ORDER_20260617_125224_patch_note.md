# R38DL Patch Note

Tag: LANE-X-R38DL_GUARDED_MISR_TRAP_ZONE_DIAG_PATCH_NO_RESTART_NO_ARM_NO_ORDER_20260617_125224
Created: 2026-06-17T12:52:25+05:30

Patched:
- app/mme_scalpx/services/feature_family/misr_surface.py

Backup:
- app/mme_scalpx/services/feature_family/misr_surface.py.r38dl_backup_20260617_125224

Patch type:
- Guarded MISR diagnostic patch.
- Default behavior unchanged.
- No threshold relaxation.
- No candidate forcing.
- No risk/execution/order path touched.
- No restart performed.

Adds MISR diagnostic fields:
- misr_trap_zone_diag_patch
- misr_trap_zone_failure_reason
- misr_trap_zone_diag

Safety:
- before streams: 0/0/0/0
- after streams: 0/0/0/0
- compile_rc: 0
