# LANE-X-R31A-R9X_MICRO_REPLAY_AFTER_RISK_ACTION_PATCH_INSPECT_EXECUTION_SHADOW_FILL_PNL_NO_ORDER_micro_replay_verify_candidate_to_risk_execution_shadow_fill_and_pnl_surfaces_20260607_225533

classification: PASS_R9X_CANDIDATE_TO_RISK_EXECUTION_SHADOW_FILL_VISIBLE_PNL_SURFACE_MISSING_NO_ORDER

## R9X purpose

Offline micro replay after R9W risk action patch. This verifies whether the full artifact chain now reaches:

1. strategy candidate true
2. candidate audit true
3. risk non-HOLD / entry allowed
4. execution-shadow non-HOLD / filled
5. PnL surfaces if available

## Replay

- replay_rc: 0
- inspect_rc: 0
- dataset_id: `LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset`
- trading_day: `2026-06-02`
- dataset_root: `run/replay/staging/LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset`
- run_root: `run/replay/lane_x_r31a_r9x/LANE-X-R31A-R9X_MICRO_REPLAY_AFTER_RISK_ACTION_PATCH_INSPECT_EXECUTION_SHADOW_FILL_PNL_NO_ORDER_micro_replay_verify_candidate_to_risk_execution_shadow_fill_and_pnl_surfaces_20260607_225533`
- artifact_root: `run/replay/lane_x_r31a_r9x/LANE-X-R31A-R9X_MICRO_REPLAY_AFTER_RISK_ACTION_PATCH_INSPECT_EXECUTION_SHADOW_FILL_PNL_NO_ORDER_micro_replay_verify_candidate_to_risk_execution_shadow_fill_and_pnl_surfaces_20260607_225533/replay_locked_single_day_lane-x-r31a-r9x_micro_replay_after_risk_action_patch_inspect_execution_shadow_fill_pnl_no_order_20260607_172535_e4d110fc`

## Artifact chain

- strategy_candidate_true: 211
- candidate_audit_true: 211
- risk_non_hold: 211
- execution_shadow_non_hold: 211
- execution_shadow_filled: 211
- execution_pnl_non_null: 0
- execution_pnl_fields_present: `{}`

## Run summary

- run_summary_candidate_count: 211
- run_summary_trade_count: 0
- run_summary_pnl_total: None

## PnL claim

- pnl_claim_allowed: False

## Safety

- post_safety_pass: True
- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- risk_proc: 0
- execution_proc: 0

## Boundary

- no patch
- offline replay only
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete

## Next decision

`PATCH_OR_AUDIT_SHADOW_PNL_EXPORT_SURFACE`
