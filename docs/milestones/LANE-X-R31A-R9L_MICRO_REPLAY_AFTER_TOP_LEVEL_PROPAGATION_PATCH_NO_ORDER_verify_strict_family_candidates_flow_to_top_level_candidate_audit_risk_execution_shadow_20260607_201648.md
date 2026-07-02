# LANE-X-R31A-R9L_MICRO_REPLAY_AFTER_TOP_LEVEL_PROPAGATION_PATCH_NO_ORDER_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648

classification: REVIEW_LANE_X_R31A_R9L_MICRO_REPLAY_CANDIDATE_FLOW_NEEDS_INSPECTION_NO_ORDER

- pre_safe: 1
- dataset_root: `run/replay/staging/LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset`
- runroot: `run/replay/lane_x_r31a_r9l/LANE-X-R31A-R9L_MICRO_REPLAY_AFTER_TOP_LEVEL_PROPAGATION_PATCH_NO_ORDER_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648`
- outdir: `run/replay/lane_x_r31a_r9l/LANE-X-R31A-R9L_MICRO_REPLAY_AFTER_TOP_LEVEL_PROPAGATION_PATCH_NO_ORDER_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648/replay_locked_single_day_lane-x-r31a-r9l_micro_replay_after_top_level_propagation_patch_no_order_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648_20260607_144649_127ee174`
- replay_started: 1
- replay_rc: 0
- smoke_rc: 0
- feature_rows: 12000
- strategy_rows: 12000
- candidate_true_rows: 0
- entry_rows: 0
- strict_candidate_sum: 0
- propagated_rows: 11789
- candidate_audit_true_rows: 0
- risk_rows: 12000
- execution_shadow_rows: 12000
- risk_non_hold_rows: 0
- execution_non_hold_rows: 0
- post_orders: 0
- post_risk_stream: 0
- post_execution_stream: 0
- replay_log: `run/logs/LANE-X-R31A-R9L_MICRO_REPLAY_AFTER_TOP_LEVEL_PROPAGATION_PATCH_NO_ORDER_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648_replay.log`
- smoke_json: `run/audits/LANE-X-R31A-R9L_MICRO_REPLAY_AFTER_TOP_LEVEL_PROPAGATION_PATCH_NO_ORDER_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648_artifact_flow.json`
- smoke_txt: `run/audits/LANE-X-R31A-R9L_MICRO_REPLAY_AFTER_TOP_LEVEL_PROPAGATION_PATCH_NO_ORDER_verify_strict_family_candidates_flow_to_top_level_candidate_audit_risk_execution_shadow_20260607_201648_artifact_flow.txt`

Interpretation:
- PASS means strict family candidates now reach top-level strategy output and candidate audit.
- If risk/execution still remain HOLD, next seam is risk adapter/decision mapping, not family strategy.
- No profitability claim until execution shadow generates fills/PnL.

Boundary: offline micro replay only; no broker order, no paper/live, no risk/execution service start, no threshold tuning, no candidate forcing.
