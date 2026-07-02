# R35B_R4C_june12_strategy_shortpath_20260613_174035

classification: REVIEW_R35B_R4C_STRATEGY_SHORTPATH_REPLAY_INCOMPLETE_NO_ORDER
proof: `run/proofs/R35B_R4C_june12_strategy_shortpath_20260613_174035.json`
dataset_root: `run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413`
run_root: `run/replay/r35b_r4c/20260613_174035`
replay_log: `run/audits/R35B_R4C_june12_strategy_shortpath_20260613_174035/replay.log`
inspect_json: `run/audits/R35B_R4C_june12_strategy_shortpath_20260613_174035/replay_inspect_summary.json`

## Safety
- PRE orders/risk/execution: 0 / 0 / 0
- POST orders/risk/execution: 0 / 0 / 0
- PRE risk/execution proc: 0 / 0
- POST risk/execution proc: 0 / 0

## RCs
- compile_rc: 0
- replay_rc: 148
- inspect_rc: 148

## Dataset shape
DATASET_ROOT=run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413
DAY=2026-06-12
RUN_ROOT=run/replay/r35b_r4c/20260613_174035

CSV row counts:
quote_ticks_mme_fut_stream.csv rows=16440
quote_ticks_mme_opt_stream.csv rows=79076

## Replay log tail
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3529, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3418, in main
    json.dumps(persisted_strategy_decisions, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
  File "/usr/lib/python3.10/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
  File "/usr/lib/python3.10/json/encoder.py", line 201, in encode
    chunks = list(chunks)
  File "/usr/lib/python3.10/json/encoder.py", line 429, in _iterencode
    yield from _iterencode_list(o, _current_indent_level)
  File "/usr/lib/python3.10/json/encoder.py", line 325, in _iterencode_list
    yield from chunks
  File "/usr/lib/python3.10/json/encoder.py", line 405, in _iterencode_dict
    yield from chunks
  File "/usr/lib/python3.10/json/encoder.py", line 405, in _iterencode_dict
    yield from chunks
  File "/usr/lib/python3.10/json/encoder.py", line 325, in _iterencode_list
    yield from chunks
  File "/usr/lib/python3.10/json/encoder.py", line 405, in _iterencode_dict
    yield from chunks
  File "/usr/lib/python3.10/json/encoder.py", line 302, in _iterencode_list
    yield buf + _encoder(value)
KeyboardInterrupt

## Inspect summary
