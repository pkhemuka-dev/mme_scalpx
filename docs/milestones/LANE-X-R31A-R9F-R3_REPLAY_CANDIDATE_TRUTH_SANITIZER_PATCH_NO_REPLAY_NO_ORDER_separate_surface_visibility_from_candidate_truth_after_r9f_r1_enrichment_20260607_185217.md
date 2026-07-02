# LANE-X-R31A-R9F-R3_REPLAY_CANDIDATE_TRUTH_SANITIZER_PATCH_NO_REPLAY_NO_ORDER_separate_surface_visibility_from_candidate_truth_after_r9f_r1_enrichment_20260607_185217

classification: REVIEW_LANE_X_R31A_R9F_R3_PATCH_OR_SMOKE_FAILED_RESTORED_IF_NEEDED_NO_REPLAY_NO_ORDER

- pre_safe: 1
- patch_rc: 0
- patch_applied: 1
- compile_rc: 0
- smoke_rc: 1
- restored: 1
- marker_count: 0
0
- sanitizer_count: 0
0
- post_orders: 0
- post_risk_stream: 0
- post_execution_stream: 0
- backup: `run/_code_backups/LANE-X-R31A-R9F-R3_REPLAY_CANDIDATE_TRUTH_SANITIZER_PATCH_NO_REPLAY_NO_ORDER_separate_surface_visibility_from_candidate_truth_after_r9f_r1_enrichment_20260607_185217_bin_replay_run.py.bak`
- patch_log: `run/audits/LANE-X-R31A-R9F-R3_REPLAY_CANDIDATE_TRUTH_SANITIZER_PATCH_NO_REPLAY_NO_ORDER_separate_surface_visibility_from_candidate_truth_after_r9f_r1_enrichment_20260607_185217_patch.log`
- smoke_log: `run/audits/LANE-X-R31A-R9F-R3_REPLAY_CANDIDATE_TRUTH_SANITIZER_PATCH_NO_REPLAY_NO_ORDER_separate_surface_visibility_from_candidate_truth_after_r9f_r1_enrichment_20260607_185217_smoke.log`

Patch doctrine:
- surface visibility remains available
- candidate_present no longer means surface exists
- strict candidate truth requires eligible=true, no blockers, score>0
- no replay, no order, no threshold tuning, no candidate forcing
