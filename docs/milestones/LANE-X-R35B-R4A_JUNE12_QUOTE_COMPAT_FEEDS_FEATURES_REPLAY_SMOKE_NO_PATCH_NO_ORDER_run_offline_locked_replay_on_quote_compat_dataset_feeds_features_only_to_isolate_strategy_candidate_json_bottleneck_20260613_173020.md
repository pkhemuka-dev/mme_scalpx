# LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020

classification: REVIEW_R35B_R4A_FEEDS_FEATURES_REPLAY_INCOMPLETE_OR_SAFETY_NOT_CLEAN_NO_ORDER
proof: `run/proofs/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020.json`
dataset_root: `run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413`
run_root: `run/replay/lane_x_r35b_june12_quote_compat_feeds_features/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020`
replay_log: `run/audits/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020/replay.log`
inspect_json: `run/audits/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020/replay_inspect_summary.json`

## Safety
- PRE orders/risk/execution: 0 / 0 / 0
- POST orders/risk/execution: 0 / 0 / 0
- PRE risk/execution proc: 0 / 0
- POST risk/execution proc: 0 / 0

## RCs
- compile_rc: 0
- replay_rc: 1
- inspect_rc: 0

## Dataset shape
DATASET_ROOT=run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413
DAY=2026-06-12

Dataset files:
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_fut_stream.csv 2285257 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/quote_ticks_mme_opt_stream.csv 11907659 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12/source_manifest.json 2330 bytes
run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/replay_dataset_declaration.json 774 bytes

CSV row counts:
quote_ticks_mme_fut_stream.csv rows=16440
quote_ticks_mme_opt_stream.csv rows=79076

## Replay log tail
Traceback (most recent call last):
  File "/usr/lib/python3.10/pathlib.py", line 1175, in mkdir
    self._accessor.mkdir(self, mode)
OSError: [Errno 36] File name too long: 'run/replay/lane_x_r35b_june12_quote_compat_feeds_features/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020/replay_locked_single_day_lane-x-r35b-r4a_june12_quote_compat_feeds_features_replay_smoke_no_patch_no_order_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020_20260613_120022_b262a0b3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3529, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3394, in main
    writer.ensure_directories(run_context.artifact_plan)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/artifacts.py", line 140, in ensure_directories
    Path(artifact_plan.root_dir).mkdir(parents=True, exist_ok=True)
  File "/usr/lib/python3.10/pathlib.py", line 1184, in mkdir
    if not exist_ok or not self.is_dir():
  File "/usr/lib/python3.10/pathlib.py", line 1305, in is_dir
    return S_ISDIR(self.stat().st_mode)
  File "/usr/lib/python3.10/pathlib.py", line 1097, in stat
    return self._accessor.stat(self, follow_symlinks=follow_symlinks)
OSError: [Errno 36] File name too long: 'run/replay/lane_x_r35b_june12_quote_compat_feeds_features/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020/replay_locked_single_day_lane-x-r35b-r4a_june12_quote_compat_feeds_features_replay_smoke_no_patch_no_order_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020_20260613_120022_b262a0b3'

## Inspect summary
{
  "csv_counts": {},
  "exists": true,
  "file_count": 0,
  "files": [],
  "json_summaries": {},
  "run_root": "run/replay/lane_x_r35b_june12_quote_compat_feeds_features/LANE-X-R35B-R4A_JUNE12_QUOTE_COMPAT_FEEDS_FEATURES_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_quote_compat_dataset_feeds_features_only_to_isolate_strategy_candidate_json_bottleneck_20260613_173020"
}