# B3-R13_REAL_CAPTURE_DATASET_PLAN_FOR_STRATEGY_REPLAY_NO_ORDER_freeze_real_capture_requirements_after_mist_call_dry_replay_closure_no_start_no_replay_no_order_20260521_150200

classification: `PASS_B3_R13_REAL_CAPTURE_DATASET_PLAN_READY_NO_ORDER`

plan_status: `REAL_CAPTURE_PLAN_READY`

## Replay state entering real capture

- B3-R10 strategy scope compatibility: `True`
- B3-R11 deterministic MIST_CALL dry replay: `True`
- B3-R12 dry replay closure: `True`

## Real captured dataset requirements

### Required streams
- ticks:mme:opt:selected:zerodha:stream or accepted provider option ticks
- ticks:mme:fut:zerodha:stream or fut_ltp present on opt rows
- features:mme:stream
- decisions:mme:stream

### Required alignment
- shared frame_id or deterministic timestamp linkage between opt_ticks, features, and decisions
- same trading_day
- same selected strategy branch window
- no stream reset/trim during capture window

### Required fields

opt_ticks:
- ts_event
- symbol
- bid
- ask
- ltp
- fut_ltp

features:
- frame_id
- frame_ts_ns
- family_features_json
- family_surfaces_json
- consumer_view_json

decisions:
- frame_id
- action
- family_id/strategy_id
- branch_id
- confidence
- activation_report_json

## First real-capture target

`MIST_CALL or MISB_CALL, one branch only`

## Next route

`B3-R14_REAL_CAPTURE_READINESS_CHECK_NO_START_NO_ORDER`

## Do not claim yet

- PnL
- live profitability
- Dhan-complete replay
- all-family replay
- production dataset admission
