# LANE-X-R35B-R1_JUNE12_PARENT_STAGE_ROOT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_retry_june12_offline_locked_replay_using_parent_stage_root_after_single_day_not_present_contract_error_20260613_171250

classification: REVIEW_R35B_R1_JUNE12_PARENT_STAGE_REPLAY_SMOKE_INCOMPLETE_OR_SAFETY_NOT_CLEAN_NO_ORDER
proof: `run/proofs/LANE-X-R35B-R1_JUNE12_PARENT_STAGE_ROOT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_retry_june12_offline_locked_replay_using_parent_stage_root_after_single_day_not_present_contract_error_20260613_171250.json`
dataset_root: `run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904`
run_root: `run/replay/lane_x_r35b_june12_single_day/LANE-X-R35B-R1_JUNE12_PARENT_STAGE_ROOT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_retry_june12_offline_locked_replay_using_parent_stage_root_after_single_day_not_present_contract_error_20260613_171250`
replay_log: `run/audits/LANE-X-R35B-R1_JUNE12_PARENT_STAGE_ROOT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_retry_june12_offline_locked_replay_using_parent_stage_root_after_single_day_not_present_contract_error_20260613_171250/replay.log`
inspect_json: `run/audits/LANE-X-R35B-R1_JUNE12_PARENT_STAGE_ROOT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_retry_june12_offline_locked_replay_using_parent_stage_root_after_single_day_not_present_contract_error_20260613_171250/replay_inspect_summary.json`

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
DATASET_ROOT=run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904
DAY=2026-06-12

Stage date dirs:
2026-06-01
2026-06-02
2026-06-03
2026-06-04
2026-06-05
2026-06-08
2026-06-09
2026-06-11
2026-06-12

Selected day files:

## Replay log tail
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/dataset.py", line 1325, in classify_replay_feed_input_source_mode_for_dataset
    validate_replay_feed_input_row(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/contracts.py", line 1505, in validate_replay_feed_input_row
    raise ValueError(
ValueError: replay feed-input row missing required fields for source_mode='economics_enriched_recorded': ('ts_event', 'symbol', 'bid', 'ask', 'ltp', 'source_frame_id', 'side', 'selected_leg', 'entry_mode', 'tick_size', 'target_ticks', 'stop_ticks', 'reward_ticks', 'reward_cost_ratio', 'economics_reason')

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3529, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3337, in main
    selection_plan = selector.build_plan(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/selectors.py", line 220, in build_plan
    "dataset_summary": dataset_summary_to_dict(dataset_summary),
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/dataset.py", line 775, in dataset_summary_to_dict
    payload = attach_replay_feed_input_contract_summary_to_dataset_summary(payload)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/dataset.py", line 1450, in attach_replay_feed_input_contract_summary_to_dataset_summary
    payload.update(classify_replay_feed_input_source_mode_for_dataset(payload))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/dataset.py", line 1333, in classify_replay_feed_input_source_mode_for_dataset
    validate_replay_feed_input_row(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/contracts.py", line 1505, in validate_replay_feed_input_row
    raise ValueError(
ValueError: replay feed-input row missing required fields for source_mode='quote_only_recorded': ('ts_event', 'symbol', 'bid', 'ask', 'ltp')

## Inspect summary
{
  "candidate_count": null,
  "csv_counts": {},
  "execution_shadow_filled": null,
  "exists": true,
  "file_count": 0,
  "files": [],
  "json_summaries": {},
  "pnl_total": null,
  "run_root": "run/replay/lane_x_r35b_june12_single_day/LANE-X-R35B-R1_JUNE12_PARENT_STAGE_ROOT_REPLAY_SMOKE_NO_PATCH_NO_ORDER_retry_june12_offline_locked_replay_using_parent_stage_root_after_single_day_not_present_contract_error_20260613_171250",
  "trade_count": null
}