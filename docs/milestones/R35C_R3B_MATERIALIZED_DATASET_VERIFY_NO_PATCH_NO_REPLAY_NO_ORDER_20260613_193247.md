# R35C_R3B_MATERIALIZED_DATASET_VERIFY_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_193247

classification: PASS_R35C_R3B_MATERIALIZED_DATASET_VERIFIED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R3B_MATERIALIZED_DATASET_VERIFY_NO_PATCH_NO_REPLAY_NO_ORDER_20260613_193247.json`
dataset_root: `run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset`

ok_days=6 bad_days=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Dataset root
run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset

## Declaration
{
  "days": {
    "2026-06-01": {
      "day": "2026-06-01",
      "fut_missing": 0,
      "fut_rows": 21229,
      "opt_missing": 0,
      "opt_rows": 110139,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260601_100637/durable_capture"
    },
    "2026-06-02": {
      "day": "2026-06-02",
      "fut_missing": 0,
      "fut_rows": 21808,
      "opt_missing": 0,
      "opt_rows": 112227,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260602_100035/durable_capture"
    },
    "2026-06-03": {
      "day": "2026-06-03",
      "fut_missing": 0,
      "fut_rows": 9698,
      "opt_missing": 0,
      "opt_rows": 50261,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260603_101759/durable_capture"
    },
    "2026-06-04": {
      "day": "2026-06-04",
      "fut_missing": 0,
      "fut_rows": 18654,
      "opt_missing": 0,
      "opt_rows": 103192,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260604_093504/durable_capture"
    },
    "2026-06-05": {
      "day": "2026-06-05",
      "fut_missing": 0,
      "fut_rows": 18658,
      "opt_missing": 0,
      "opt_rows": 99424,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260605_091243/durable_capture"
    },
    "2026-06-12": {
      "day": "2026-06-12",
      "fut_missing": 0,
      "fut_rows": 16440,
      "opt_missing": 0,
      "opt_rows": 79076,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture"
    }
  },
  "schema_version": "r35c_r3a_quote_dataset_v1"
}
## Day file verification
DAY=2026-06-01 fut_lines=21230 opt_lines=110140 fut_size=3736352 opt_size=20109951 manifest=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-01/source_manifest.json
DAY=2026-06-02 fut_lines=21809 opt_lines=112228 fut_size=3838256 opt_size=20362775 manifest=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-02/source_manifest.json
DAY=2026-06-03 fut_lines=9699 opt_lines=50262 fut_size=1706896 opt_size=9265317 manifest=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-03/source_manifest.json
DAY=2026-06-04 fut_lines=18655 opt_lines=103193 fut_size=3283152 opt_size=19023962 manifest=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-04/source_manifest.json
DAY=2026-06-05 fut_lines=18659 opt_lines=99425 fut_size=3283856 opt_size=18314592 manifest=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-05/source_manifest.json
DAY=2026-06-12 fut_lines=16441 opt_lines=79077 fut_size=2893488 opt_size=14517118 manifest=run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-12/source_manifest.json

ok_days=6
bad_days=0

## Dataset largest files
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
