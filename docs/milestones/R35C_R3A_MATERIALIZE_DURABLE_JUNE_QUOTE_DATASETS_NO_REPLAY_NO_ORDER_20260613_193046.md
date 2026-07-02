# R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046

classification: PASS_R35C_R3A_DURABLE_JUNE_QUOTE_DATASETS_MATERIALIZED_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046.json`
dataset_root: `run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset`

build_rc=0 ok_days=6
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Build log
{"day": "2026-06-01", "fut_missing": 0, "fut_rows": 21229, "opt_missing": 0, "opt_rows": 110139, "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260601_100637/durable_capture"}
{"day": "2026-06-02", "fut_missing": 0, "fut_rows": 21808, "opt_missing": 0, "opt_rows": 112227, "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260602_100035/durable_capture"}
{"day": "2026-06-03", "fut_missing": 0, "fut_rows": 9698, "opt_missing": 0, "opt_rows": 50261, "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260603_101759/durable_capture"}
{"day": "2026-06-04", "fut_missing": 0, "fut_rows": 18654, "opt_missing": 0, "opt_rows": 103192, "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260604_093504/durable_capture"}
{"day": "2026-06-05", "fut_missing": 0, "fut_rows": 18658, "opt_missing": 0, "opt_rows": 99424, "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260605_091243/durable_capture"}
{"day": "2026-06-12", "fut_missing": 0, "fut_rows": 16440, "opt_missing": 0, "opt_rows": 79076, "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture"}
OUT=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset

## Output sizes
20362775 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-02/quote_ticks_mme_opt_stream.csv
20109951 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-01/quote_ticks_mme_opt_stream.csv
19023962 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-04/quote_ticks_mme_opt_stream.csv
18314592 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-05/quote_ticks_mme_opt_stream.csv
14517118 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-12/quote_ticks_mme_opt_stream.csv
9265317 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-03/quote_ticks_mme_opt_stream.csv
3838256 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-02/quote_ticks_mme_fut_stream.csv
3736352 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-01/quote_ticks_mme_fut_stream.csv
3283856 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-05/quote_ticks_mme_fut_stream.csv
3283152 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-04/quote_ticks_mme_fut_stream.csv
2893488 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-12/quote_ticks_mme_fut_stream.csv
1706896 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-03/quote_ticks_mme_fut_stream.csv
1683 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/replay_dataset_declaration.json
222 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-04/source_manifest.json
222 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-02/source_manifest.json
222 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-01/source_manifest.json
221 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-12/source_manifest.json
221 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-05/source_manifest.json
220 run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-03/source_manifest.json

## Build errors
