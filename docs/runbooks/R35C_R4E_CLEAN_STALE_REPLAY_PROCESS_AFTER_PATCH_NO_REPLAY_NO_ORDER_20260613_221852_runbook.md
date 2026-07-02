# R35C_R4E_CLEAN_STALE_REPLAY_PROCESS_AFTER_PATCH_NO_REPLAY_NO_ORDER_20260613_221852

classification: REVIEW_R35C_R4E_STALE_REPLAY_PROCESS_STILL_PRESENT_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4E_CLEAN_STALE_REPLAY_PROCESS_AFTER_PATCH_NO_REPLAY_NO_ORDER_20260613_221852.json`

safety orders=0 risk=0 execution=0 proc=0/0 replay_proc=2

## Before
## jobs before
[1]+ 258330 Stopped                 timeout 900s "$PY" bin/replay_run.py --dataset-root "$D" --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4d_20260601_summary_patch_verify --dataset-id r35c_r4d --run-root "$RR" --recurse > "$LOG" 2>&1

## processes before
 258330  257971 T          04:37 timeout 900s .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4d_20260601_summary_patch_verify --dataset-id r35c_r4d --run-root run/replay/r35c_r4d/20260613_221414 --recurse
 258331  258330 T          04:37 .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4d_20260601_summary_patch_verify --dataset-id r35c_r4d --run-root run/replay/r35c_r4d/20260613_221414 --recurse

## After
## processes after
 258330  257971 T          04:40 timeout 900s .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4d_20260601_summary_patch_verify --dataset-id r35c_r4d --run-root run/replay/r35c_r4d/20260613_221414 --recurse
 258331  258330 T          04:40 .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4d_20260601_summary_patch_verify --dataset-id r35c_r4d --run-root run/replay/r35c_r4d/20260613_221414 --recurse

## jobs after
[1]+ 258330 Stopped                 timeout 900s "$PY" bin/replay_run.py --dataset-root "$D" --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4d_20260601_summary_patch_verify --dataset-id r35c_r4d --run-root "$RR" --recurse > "$LOG" 2>&1
