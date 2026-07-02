# LANE-X-R35B_JUNE12_SINGLE_DAY_BOUNDED_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_size_graded_june12_stage_first_before_full_june_backtest_20260613_171145

classification: REVIEW_R35B_JUNE12_REPLAY_SMOKE_INCOMPLETE_OR_SAFETY_NOT_CLEAN_NO_ORDER
proof: `run/proofs/LANE-X-R35B_JUNE12_SINGLE_DAY_BOUNDED_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_size_graded_june12_stage_first_before_full_june_backtest_20260613_171145.json`
dataset_root: `run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12`
run_root: `run/replay/lane_x_r35b_june12_single_day/LANE-X-R35B_JUNE12_SINGLE_DAY_BOUNDED_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_size_graded_june12_stage_first_before_full_june_backtest_20260613_171145`
replay_log: `run/audits/LANE-X-R35B_JUNE12_SINGLE_DAY_BOUNDED_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_size_graded_june12_stage_first_before_full_june_backtest_20260613_171145/replay.log`
inspect_json: `run/audits/LANE-X-R35B_JUNE12_SINGLE_DAY_BOUNDED_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_size_graded_june12_stage_first_before_full_june_backtest_20260613_171145/replay_inspect_summary.json`

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
DATASET_ROOT=run/staging/LANE-X-R35B0-R3_JUNE_STAGING_SIZE_QUALITY_REPAIR_NO_PATCH_NO_REPLAY_NO_ORDER_grade_r35b0_r2_stage_by_file_size_and_rebuild_preferred_stage_using_durable_when_pseal_streams_are_tiny_20260613_170904/2026-06-12

## Replay log tail
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3529, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3337, in main
    selection_plan = selector.build_plan(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/selectors.py", line 207, in build_plan
    selected_dates = self._resolve_dates(request, available_dates)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/selectors.py", line 253, in _resolve_dates
    raise ReplaySelectionUnavailableError(
app.mme_scalpx.replay.selectors.ReplaySelectionUnavailableError: requested single_day not present in dataset: 2026-06-12

## Inspect summary
{
  "candidate_count": null,
  "csv_counts": {},
  "execution_shadow_filled": null,
  "exists": true,
  "files": [],
  "json_summaries": {},
  "pnl_total": null,
  "risk_non_hold": null,
  "run_root": "run/replay/lane_x_r35b_june12_single_day/LANE-X-R35B_JUNE12_SINGLE_DAY_BOUNDED_REPLAY_SMOKE_NO_PATCH_NO_ORDER_run_offline_locked_replay_on_size_graded_june12_stage_first_before_full_june_backtest_20260613_171145",
  "trade_count": null
}