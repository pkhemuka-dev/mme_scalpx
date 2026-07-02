# LANE-X-R31A-R9U_MICRO_REPLAY_AFTER_BRIDGE_PATCH_INSPECT_CANDIDATE_AUDIT_RISK_EXECUTION_SHADOW_NO_ORDER_micro_replay_inspect_20260607_224505

classification: PASS_R9U_CANDIDATE_POSITIVE_TO_AUDIT_RISK_EXECUTION_SHADOW_ROWS_VISIBLE_NO_ORDER

## R9U purpose

Offline micro replay after R9T-R3B bridge patch seal. This inspects whether candidate-positive bridge rows now flow into:

1. `strategy_decisions.json`
2. `06_candidate_audit.csv`
3. `risk_outputs.json`
4. `execution_shadow_results.json`

No PnL claim is made.

## Replay

- replay_rc: 0
- inspect_rc: 0
- dataset_id: `LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset`
- trading_day: `2026-06-02`
- dataset_root: `run/replay/staging/LANE-X-R31A-R9H_MICRO_REPLAY_DATASET_SLICE_BUILD_NO_PATCH_NO_REPLAY_NO_ORDER_build_tiny_dataset_slice_for_fast_family_bridge_replay_smoke_without_touching_source_dataset_20260607_193229_micro_dataset`
- run_root: `run/replay/lane_x_r31a_r9u/LANE-X-R31A-R9U_MICRO_REPLAY_AFTER_BRIDGE_PATCH_INSPECT_CANDIDATE_AUDIT_RISK_EXECUTION_SHADOW_NO_ORDER_micro_replay_inspect_20260607_224505`
- artifact_root: `run/replay/lane_x_r31a_r9u/LANE-X-R31A-R9U_MICRO_REPLAY_AFTER_BRIDGE_PATCH_INSPECT_CANDIDATE_AUDIT_RISK_EXECUTION_SHADOW_NO_ORDER_micro_replay_inspect_20260607_224505/replay_locked_single_day_lane-x-r31a-r9u_micro_replay_after_bridge_patch_inspect_candidate_audit_risk_execution_shadow_no_order_20260607_171507_4beaa416`

## Candidate-positive chain

- strategy_candidate_true: 211
- strategy_strict_total: 633
- strategy_misb_strict_total: 633
- candidate_audit_true: 211
- candidate_audit_rows: 12000
- risk_rows: 12000
- risk_non_hold: 0
- execution_shadow_rows: 12000
- execution_shadow_non_hold: 0
- execution_shadow_filled: 0
- bridge_status_counts: `{'adapter_payload_used': 12000}`
- bridge_error_counts: `{}`

## Run summary

- run_summary_candidate_count: 211
- run_summary_trade_count: 0
- run_summary_pnl_total: None

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
- no PnL claim yet

## Next decision

`AUDIT_EXECUTION_SHADOW_ACTION_MAPPING_BEFORE_PNL_CLAIM`
