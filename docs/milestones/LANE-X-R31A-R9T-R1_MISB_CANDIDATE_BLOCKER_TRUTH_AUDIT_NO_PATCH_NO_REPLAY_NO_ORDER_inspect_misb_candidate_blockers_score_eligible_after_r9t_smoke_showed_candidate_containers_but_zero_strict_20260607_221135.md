# LANE-X-R31A-R9T-R1_MISB_CANDIDATE_BLOCKER_TRUTH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_misb_candidate_blockers_score_eligible_after_r9t_smoke_showed_candidate_containers_but_zero_strict_20260607_221135

classification: PASS_LANE_X_R31A_R9T_R1_MISB_CANDIDATE_BLOCKER_TRUTH_AUDIT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- rows_with_misb_breakout: 14
- rows_with_adapter_misb: 500
- misb_candidate_total: 1000
- strict_candidate_total: 13
- output_json: `run/audits/LANE-X-R31A-R9T-R1_MISB_CANDIDATE_BLOCKER_TRUTH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_misb_candidate_blockers_score_eligible_after_r9t_smoke_showed_candidate_containers_but_zero_strict_20260607_221135_misb_blocker_truth.json`
- output_text: `run/audits/LANE-X-R31A-R9T-R1_MISB_CANDIDATE_BLOCKER_TRUTH_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_misb_candidate_blockers_score_eligible_after_r9t_smoke_showed_candidate_containers_but_zero_strict_20260607_221135_misb_blocker_truth.txt`

Decision:
- If blockers are breakout-trigger false despite surface true, patch adapter surface lookup.
- If blockers are economics/spread/reward-cost, patch replay economics mapping only after proof.
- If strict candidates appear direct adapter but not replay_run, patch bridge merge.

Boundary: no patch, no replay, no order.
