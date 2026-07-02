# R35B_R4T_RECOVER_AND_STOP_STALE_R4F_REPLAY_NO_ORDER_20260613_192100

classification: PASS_R35B_R4T_ARTIFACT_CAP_RECOVERED_AND_STALE_R4F_STOPPED_NO_ORDER
proof: `run/proofs/R35B_R4T_RECOVER_AND_STOP_STALE_R4F_REPLAY_NO_ORDER_20260613_192100.json`
r4t_root: `run/replay/r35b_r4t/20260613_191656`

big_files_over_50mb=0
stale_r4f_pids_killed=256303 
r4f_left=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## R4T largest files
11468 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/02_scope_profile.json
10361 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/artifacts/economics_summary.json
6543 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/01_dataset_summary.json
4977 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/artifacts/engine_result.json
3738 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/00_manifest.json
2307 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/17_effective_inputs.json
751 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/artifacts/b3_r32_analysis_exports_status.json
269 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/18_effective_overrides_flat.json
202 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/06_candidate_audit.csv
113 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/artifacts/blocker_distribution.csv
81 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/artifacts/family_side_summary.csv
59 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/04_metrics_summary.json
55 run/replay/r35b_r4t/20260613_191656/replay_locked_single_day_r35b_r4t_20260613_134659_f8a750e5/03_integrity_report.json

## Process before
## before processes
 256303  254863    01:29:43 timeout 900s .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413 --selection-mode single_day --single-day 2026-06-12 --doctrine-mode locked --scope feeds_features_strategy --speed-mode accelerated --run-label r35b_r4f_strategy --dataset-id r35b_r4f --run-root run/replay/r35b_r4f/20260613_175116 --recurse

## Process after
## after processes
 256303  254863    01:29:45 timeout 900s .venv/bin/python bin/replay_run.py --dataset-root run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413 --selection-mode single_day --single-day 2026-06-12 --doctrine-mode locked --scope feeds_features_strategy --speed-mode accelerated --run-label r35b_r4f_strategy --dataset-id r35b_r4f --run-root run/replay/r35b_r4f/20260613_175116 --recurse
