# LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913

classification: REVIEW_R35B_R3_QUOTE_COMPAT_BUILD_INCOMPLETE_OR_SAFETY_NOT_CLEAN_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913.json`
src_root: `run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904`
dst_root: `run/replay/staging/LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913`
build_log: `run/audits/LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913/build_quote_compat.log`
inspect_json: `run/audits/LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913/quote_compat_dataset_inspect.json`

## Safety
- PRE orders/risk/execution: 0 / 0 / 0
- POST orders/risk/execution: 0 / 0 / 0
- PRE risk/execution proc: 0 / 0
- POST risk/execution proc: 0 / 0

## RCs
- compile_rc: 0
- build_rc: 1
- inspect_rc: 0

## Source shape
SRC_ROOT=run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904
SRC_DAY=2026-06-12
DST_ROOT=run/replay/staging/LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913

Source day listing:
decisions.jsonl.gz 152 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/decisions.jsonl.gz
errors.jsonl.gz 149 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/errors.jsonl.gz
features.jsonl.gz 151 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/features.jsonl.gz
fut_zerodha.jsonl.gz 154 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/fut_zerodha.jsonl.gz
health.jsonl.gz 149 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/health.jsonl.gz
heartbeat.json 148 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/heartbeat.json
manifest_start.json 153 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/manifest_start.json
manifest_stop.json 152 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/manifest_stop.json
opt_selected_zerodha.jsonl.gz 163 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/opt_selected_zerodha.jsonl.gz
provider_runtime.jsonl.gz 159 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/provider_runtime.jsonl.gz
recorder.log 146 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/recorder.log
recorder_errors.log 153 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/recorder_errors.log
state.json 144 bytes -> /home/Lenovo/scalpx/projects/mme_scalpx/run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture/state.json

## Build log tail
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/build_replay_quote_compat_dataset.py", line 151, in <module>
    raise SystemExit(main())
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/build_replay_quote_compat_dataset.py", line 120, in main
    raise FileNotFoundError(src)
FileNotFoundError: /home/Lenovo/scalpx/projects/mme_scalpx/run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12/ticks_mme_fut_stream.csv

## Dataset inspect
{
  "csv_preview": {},
  "date_dirs": [],
  "dst_root": "run/replay/staging/LANE-X-R35B-R3_BUILD_JUNE12_QUOTE_COMPAT_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_materialize_june12_size_graded_stage_into_quote_compatible_replay_dataset_before_replay_retry_20260613_171913",
  "exists": true,
  "file_count": 0,
  "files": [],
  "json_preview": {}
}