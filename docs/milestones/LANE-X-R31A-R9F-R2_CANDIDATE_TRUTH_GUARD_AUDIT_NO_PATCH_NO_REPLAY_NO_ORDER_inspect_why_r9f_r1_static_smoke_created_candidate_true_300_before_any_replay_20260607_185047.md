# LANE-X-R31A-R9F-R2_CANDIDATE_TRUTH_GUARD_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_why_r9f_r1_static_smoke_created_candidate_true_300_before_any_replay_20260607_185047

classification: PASS_LANE_X_R31A_R9F_R2_CANDIDATE_TRUTH_GUARD_AUDIT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- candidate_present_total_estimate: 45
- eligible_total_estimate: 45
- surface_non_empty_total_estimate: 45
- main_hint: LIKELY_ADAPTER_TREATS_NON_EMPTY_SURFACE_AS_CANDIDATE_PRESENT
- output: `run/audits/LANE-X-R31A-R9F-R2_CANDIDATE_TRUTH_GUARD_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_why_r9f_r1_static_smoke_created_candidate_true_300_before_any_replay_20260607_185047_candidate_truth_guard_audit.txt`

Decision:
- If candidate_present is true merely because surface exists, do not replay.
- Next patch must separate surface visibility from candidate truth.
- Candidate truth must require actual doctrine boolean chain, not just non-empty surface.

Boundary: no patch, no replay, no order.
