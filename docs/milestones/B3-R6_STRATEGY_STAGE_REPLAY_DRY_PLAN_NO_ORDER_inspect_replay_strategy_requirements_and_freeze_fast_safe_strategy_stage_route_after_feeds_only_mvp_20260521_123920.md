# B3-R6_STRATEGY_STAGE_REPLAY_DRY_PLAN_NO_ORDER_inspect_replay_strategy_requirements_and_freeze_fast_safe_strategy_stage_route_after_feeds_only_mvp_20260521_123920

classification: `PASS_B3_R6_STRATEGY_STAGE_REPLAY_DRY_PLAN_READY_NO_ORDER`

strategy_readiness: `PLAN_READY_NOT_EXECUTION_READY`

## Where we are

B3-R5 closed feeds-only replay MVP. That proves deterministic offline replay CLI/dataset-selection/feed-stage path, but it does not prove strategy replay or PnL.

## Why strategy replay is not executed yet

- Current accepted MVP dataset has only 2 quote-only rows.
- Current source_mode is quote_only_recorded.
- feed_input_economics_evaluable=false in B3-R4G output.
- B3-R5 explicitly says not full strategy replay and no PnL validity claim.
- Dhan-complete replay readiness is not proved.
- Production-grade dataset admission is not proved.

## Minimum surfaces needed next

- opt_ticks.jsonl or equivalent feed input accepted by replay
- feature rows or feature-buildable feed rows
- family_features_json / family_surfaces_json or replay feature builder path
- decision rows or strategy replay stage enabled
- strategy action/candidate metadata
- session/trading-day manifest

## Fast safe route

1. B3-R7: create strategy-stage dataset requirements adapter/readiness proof.
2. B3-R8: one-strategy dry execution only, no broker/order/PnL.
3. B3-R9: deterministic rerun proof.
4. B3-R10: expand to family coverage only after one-strategy dry pass.

## Recommended first target

Start with one branch only, preferably MIST or MISB, because they are simpler than MISO/Dhan-context-driven paths.

## Next route

`B3-R7_STRATEGY_STAGE_DATASET_REQUIREMENTS_ADAPTER_NO_REPLAY_NO_ORDER`
