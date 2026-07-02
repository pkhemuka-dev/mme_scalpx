# LANE-X-R31A-R9F-R7_STRATEGY_ADAPTER_CANDIDATE_PRESENT_SOURCE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_candidate_present_assignment_in_replay_strategy_adapter_before_truth_patch_20260607_190933

classification: PASS_LANE_X_R31A_R9F_R7_STRATEGY_ADAPTER_CANDIDATE_PRESENT_SOURCE_LOCATED_NO_PATCH_NO_REPLAY_NO_ORDER

- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- candidate_present_source_count: 2
- eligible_source_count: 9
- score_source_count: 14
- output: `run/audits/LANE-X-R31A-R9F-R7_STRATEGY_ADAPTER_CANDIDATE_PRESENT_SOURCE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_candidate_present_assignment_in_replay_strategy_adapter_before_truth_patch_20260607_190933_strategy_adapter_candidate_present_source.txt`

Decision:
- Next patch should modify candidate_present at source in strategy_adapter.py.
- Do not replay until candidate_present means strict candidate truth.
- Surface visibility must remain available, but separate from candidate truth.

Boundary: no patch, no replay, no order.
