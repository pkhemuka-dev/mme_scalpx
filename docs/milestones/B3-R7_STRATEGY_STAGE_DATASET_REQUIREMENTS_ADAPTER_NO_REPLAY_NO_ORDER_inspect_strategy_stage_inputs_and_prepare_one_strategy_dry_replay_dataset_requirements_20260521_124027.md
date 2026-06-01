# B3-R7_STRATEGY_STAGE_DATASET_REQUIREMENTS_ADAPTER_NO_REPLAY_NO_ORDER_inspect_strategy_stage_inputs_and_prepare_one_strategy_dry_replay_dataset_requirements_20260521_124027

classification: `PASS_B3_R7_STRATEGY_STAGE_DATASET_REQUIREMENTS_READY_FOR_ADAPTER_BUILD_NO_ORDER`

adapter_status: `REQUIREMENTS_READY_NOT_REPLAY_EXECUTION_READY`

## Strategy-stage replay dataset requirement result

Prior chain:
- B3-R4G feeds-only deterministic replay MVP: `True`
- B3-R5 feeds-only closure: `True`
- B3-R6 strategy-stage plan: `True`

## Required surfaces

### Feed stage
- status: `available_from_B3_R4G`
- accepted file: `opt_ticks.jsonl`

### Feature stage
- status: `needs_adapter_or_capture`
- required fields:
  - frame_id
  - frame_ts_ns or ts_event
  - consumer_view_json or reconstructed consumer view
  - family_features_json
  - family_surfaces_json
  - schema_version

### Strategy stage
- status: `needs_adapter_or_strategy_replay_stage`
- required fields:
  - action
  - branch_id
  - family_id or strategy_id
  - confidence
  - activation_report_json or candidate metadata
  - frame_id / linked feature frame

### Economics / PnL
- status: `explicitly_not_ready`
- Do not test PnL yet.

## Next route

`B3-R8_ONE_STRATEGY_FEATURE_DECISION_ADAPTER_DRY_RUN_NO_ORDER`

## Recommendation

Build B3-R8 as one-branch dry adapter only. Prefer MIST or MISB. Do not run all-family or PnL.
