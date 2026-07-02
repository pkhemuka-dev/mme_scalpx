# LANE-X-R31A-R9J_STRICT_CANDIDATE_FLOW_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_211_strict_nested_candidates_why_not_reaching_run_summary_candidate_audit_risk_execution_shadow_20260607_193810

classification: PASS_LANE_X_R31A_R9J_STRICT_CANDIDATE_FLOW_AUDIT_COMPLETED_NO_PATCH_NO_REPLAY_NO_ORDER

- audit_rc: 0
- orders: 0
- risk_stream: 0
- execution_stream: 0
- replay_proc: 0
- strict_nested_count: 211
- top_level_true_count: 0
- candidate_audit_rows: 12000
- candidate_audit_true_rows: 0
- risk_rows: 12000
- execution_shadow_rows: 12000
- output_json: `run/audits/LANE-X-R31A-R9J_STRICT_CANDIDATE_FLOW_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_211_strict_nested_candidates_why_not_reaching_run_summary_candidate_audit_risk_execution_shadow_20260607_193810_strict_candidate_flow.json`
- output_text: `run/audits/LANE-X-R31A-R9J_STRICT_CANDIDATE_FLOW_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_211_strict_nested_candidates_why_not_reaching_run_summary_candidate_audit_risk_execution_shadow_20260607_193810_strict_candidate_flow.txt`

Decision:
- If strict_nested_count > 0 but top_level_true_count = 0, next patch is selected-family/top-level candidate propagation.
- If top-level candidate exists but candidate_audit/run_summary ignore it, next patch is export/summary propagation.
- No PnL claim until execution_shadow consumes candidate truth.

Boundary: no patch, no replay, no order, no paper/live, no risk/execution.
