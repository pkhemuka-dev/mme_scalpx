# LANE-X-R31A-R7_FAMILY_CANDIDATE_BRIDGE_ROOT_CAUSE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_where_family_identity_r26_r27_fields_candidate_truth_are_lost_between_features_strategy_risk_20260607_175914

classification: PASS_LANE_X_R31A_R7_FAMILY_CANDIDATE_BRIDGE_ROOT_CAUSE_LOCATED_NO_PATCH_NO_REPLAY_NO_ORDER

- main_hint: FAMILY_IDENTITY_NOT_REACHING_STRATEGY_OR_CANDIDATE_AUDIT
- feature_r26: 0
- strategy_r26: 0
- feature_r27: 0
- strategy_r27: 0
- feature_family: 0
- strategy_family: 0
- candidate_family: 0
- strategy_candidate_true: 536140
- candidate_true: 0
- risk_allow: 134035
- no_entry_strategy: 402105
- output: `run/audits/LANE-X-R31A-R7_FAMILY_CANDIDATE_BRIDGE_ROOT_CAUSE_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_where_family_identity_r26_r27_fields_candidate_truth_are_lost_between_features_strategy_risk_20260607_175914_bridge_locator.txt`

Decision:
- If R26/R27 fields are present in features but missing in strategy, patch bridge passthrough.
- If family identity is missing in strategy/candidate audit, patch family decode/strategy decision export.
- If all rows become no_entry_condition before family evaluator, patch replay strategy-family invocation.

Boundary: no patch, no replay, no order.
