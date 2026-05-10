# 2026-05-10 — 26-O23-Q-R6

Verdict: `FAIL_O23_Q_R6_EXTRACTOR_MAPPING_PATCH_PLAN_NOT_PROVEN`

## Extractor mapping plan
- classification: `Q_R6_EXACT_EXTRACTOR_PATCH_PLAN_READY_FROM_Q_R5_SURFACE_CANDIDATE_PATHS`
- candidate_path_count: `16`
- valid_candidate_count: `16`
- scope_count: `10`
- scope_counter: `{'MIST_CALL': 16, 'MIST_PUT': 16, 'MISB_CALL': 16, 'MISB_PUT': 16, 'MISC_CALL': 16, 'MISC_PUT': 16, 'MISR_CALL': 16, 'MISR_PUT': 16, 'MISO_CALL': 16, 'MISO_PUT': 16}`
- proposed_diff: `run/live_capture/batch26o23_q_r6_extractor_mapping_patch_plan_20260510_115134/o23q_r6_proposed_q_r7_corrected_extractor.diff`

## Safety
- source_patch_applied: `False`
- service_start_attempted: `False`
- paper_start_attempted: `False`
- real_live_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`

Next: 26-O23-Q-R7 apply corrected extractor/ranking logic in diagnostic batch only, rerun family surface ranking from existing payload; no production source patch unless Q-R7 proves exact target; no paper/live.
