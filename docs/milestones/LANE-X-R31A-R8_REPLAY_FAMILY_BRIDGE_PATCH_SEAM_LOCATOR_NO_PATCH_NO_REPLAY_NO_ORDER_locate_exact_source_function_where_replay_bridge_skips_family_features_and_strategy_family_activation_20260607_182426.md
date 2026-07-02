# LANE-X-R31A-R8_REPLAY_FAMILY_BRIDGE_PATCH_SEAM_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_source_function_where_replay_bridge_skips_family_features_and_strategy_family_activation_20260607_182426

classification: PASS_LANE_X_R31A_R8_REPLAY_FAMILY_BRIDGE_PATCH_SEAM_LOCATED_NO_PATCH_NO_REPLAY_NO_ORDER

- orders: 0
- risk_stream: 0
- execution_stream: 0
- seam_hint: FOUND_REPLAY_BRIDGE_V3_EVENT_NORMALIZED_SOURCE
- family_invocation_present: 1
- family_scope_export_present: 1
- source_locator: `run/audits/LANE-X-R31A-R8_REPLAY_FAMILY_BRIDGE_PATCH_SEAM_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_locate_exact_source_function_where_replay_bridge_skips_family_features_and_strategy_family_activation_20260607_182426_patch_seam_locator.txt`

Interpretation:
- We need patch the replay family bridge, not thresholds.
- Target is the seam where replay creates generic feature frames / decisions without family id, R26/R27 fields, or strategy-family activation output.
- Next batch should be R31A-R9 patch package after reviewing this locator output.

Boundary: no patch, no replay, no order.
