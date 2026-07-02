# R35C_R4F_CLEAN_STOPPED_REPLAY_JOB_NO_REPLAY_NO_ORDER_20260613_222505

classification: PASS_R35C_R4F_STOPPED_REPLAY_JOB_CLEANED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4F_CLEAN_STOPPED_REPLAY_JOB_NO_REPLAY_NO_ORDER_20260613_222505.json`

safety orders=0 risk=0 execution=0 proc=0/0 replay_proc=0

## Before
## before jobs
[1]+ 258533 Stopped                 timeout 900s "$PY" bin/replay_run.py --dataset-root "$D" --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4f_20260601 --dataset-id r35c_r4f --run-root "$RR" --recurse > "$LOG" 2>&1

## before processes
 258533  257971 T          02:51 timeout 900s .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4f_20260601 --dataset-id r35c_r4f --run-root run/replay/r35c_r4f/20260613_222214 --recurse
 258534  258533 T          02:51 .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset --selection-mode single_day --single-day 2026-06-01 --doctrine-mode locked --scope feeds_features_strategy_risk_execution_shadow --speed-mode accelerated --run-label r35c_r4f_20260601 --dataset-id r35c_r4f --run-root run/replay/r35c_r4f/20260613_222214 --recurse

## After
## after processes

## after jobs
