# LANE-X-R35A-R3_REPLAY_RUNNER_CONTRACT_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_current_replay_runner_help_entrypoint_and_prior_r9x_invocation_before_bounded_june_backtest_20260613_164918

classification: PASS_R35A_R3_REPLAY_RUNNER_CONTRACT_CAPTURED_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R35A-R3_REPLAY_RUNNER_CONTRACT_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_current_replay_runner_help_entrypoint_and_prior_r9x_invocation_before_bounded_june_backtest_20260613_164918.json`
audit: `run/audits/LANE-X-R35A-R3_REPLAY_RUNNER_CONTRACT_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_current_replay_runner_help_entrypoint_and_prior_r9x_invocation_before_bounded_june_backtest_20260613_164918`

## Safety
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0
- danger_hits: 2

## Runner help
============================================================
HELP: bin/replay_run.py --help
usage: replay_run.py [-h] --dataset-root DATASET_ROOT --selection-mode
                     {single_day,date_range,custom_date_list,intraday_window,session_segment,weekday_batch,monthly_batch}
                     [--single-day SINGLE_DAY] [--start-date START_DATE]
                     [--end-date END_DATE] [--custom-dates CUSTOM_DATES]
                     [--weekdays WEEKDAYS] [--months MONTHS]
                     [--window-start WINDOW_START] [--window-end WINDOW_END]
                     [--session-segment SESSION_SEGMENT] --doctrine-mode
                     {locked,shadow,differential} --scope
                     {feeds_only,feeds_features,feeds_features_strategy,feeds_features_strategy_risk,feeds_features_strategy_risk_execution_shadow,full_system_replay}
                     [--speed-mode {accelerated,realtime_1x,paused,step,breakpoint}]
                     [--run-label RUN_LABEL]
                     [--experiment-profile EXPERIMENT_PROFILE]
                     [--override-pack-id OVERRIDE_PACK_ID]
                     [--dataset-id DATASET_ID] [--fill-model FILL_MODEL]
                     [--run-root RUN_ROOT]
                     [--required-file-stems REQUIRED_FILE_STEMS]
                     [--optional-file-stems OPTIONAL_FILE_STEMS]
                     [--supported-suffixes SUPPORTED_SUFFIXES] [--recurse]
                     [--clock-start-time CLOCK_START_TIME]
                     [--channel-prefix CHANNEL_PREFIX]
                     [--allow-option-only-fut-context]

Run one frozen replay backbone execution.

options:
  -h, --help            show this help message and exit
  --dataset-root DATASET_ROOT
                        Replay dataset root directory
  --selection-mode {single_day,date_range,custom_date_list,intraday_window,session_segment,weekday_batch,monthly_batch}
                        Canonical replay selection mode
  --single-day SINGLE_DAY
                        YYYY-MM-DD for single_day / intraday_window /
                        session_segment
  --start-date START_DATE
                        YYYY-MM-DD for date_range
  --end-date END_DATE   YYYY-MM-DD for date_range
  --custom-dates CUSTOM_DATES
                        Comma-separated YYYY-MM-DD list for custom_date_list
  --weekdays WEEKDAYS   Comma-separated weekday integers 0..6 for
                        weekday_batch
  --months MONTHS       Comma-separated month integers 1..12 for monthly_batch
  --window-start WINDOW_START
                        HH:MM[:SS] intraday window start
  --window-end WINDOW_END
                        HH:MM[:SS] intraday window end
  --session-segment SESSION_SEGMENT
                        Named session segment for session_segment mode
  --doctrine-mode {locked,shadow,differential}
                        locked or shadow
  --scope {feeds_only,feeds_features,feeds_features_strategy,feeds_features_strategy_risk,feeds_features_strategy_risk_execution_shadow,full_system_replay}
                        Replay topology scope
  --speed-mode {accelerated,realtime_1x,paused,step,breakpoint}
                        Replay clock speed mode
  --run-label RUN_LABEL
  --experiment-profile EXPERIMENT_PROFILE
  --override-pack-id OVERRIDE_PACK_ID
  --dataset-id DATASET_ID
  --fill-model FILL_MODEL
  --run-root RUN_ROOT
  --required-file-stems REQUIRED_FILE_STEMS
  --optional-file-stems OPTIONAL_FILE_STEMS
  --supported-suffixes SUPPORTED_SUFFIXES
  --recurse
  --clock-start-time CLOCK_START_TIME
                        Replay clock start time in ISO-8601
  --channel-prefix CHANNEL_PREFIX
                        Logical replay channel prefix for feed injections
  --allow-option-only-fut-context
                        Replay staging-only compatibility: allow opt_ticks
                        rows carrying fut_ltp as disabled-by-default synthetic
                        futures context when fut_ticks is absent/empty.
RC=0
============================================================
HELP: bin/replay_batch.py --help
usage: replay_batch.py [-h] --scope
                       {single_day,date_range,date_list,intraday_window,scenario_matrix}
                       [--day DAY] [--start-date START_DATE]
                       [--end-date END_DATE] [--dates [DATES ...]]
                       [--start-time START_TIME] [--end-time END_TIME]
                       [--scenario SCENARIO] [--out-root OUT_ROOT] [--dry-run]

Replay-only batch runner. Does not touch live Redis or brokers.

options:
  -h, --help            show this help message and exit
  --scope {single_day,date_range,date_list,intraday_window,scenario_matrix}
  --day DAY
  --start-date START_DATE
  --end-date END_DATE
  --dates [DATES ...]
  --start-time START_TIME
  --end-time END_TIME
  --scenario SCENARIO
  --out-root OUT_ROOT
  --dry-run
RC=0

## Prior R9X invocation locator
============================================================
Prior R9X invocation / effective inputs locator
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:3:  "artifact_root": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:24:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:37:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:52:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:69:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:85:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:157:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:169:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:188:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:199:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:218:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:233:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:250:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:269:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:290:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:310:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:434:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:444:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:452:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928"
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:458:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:799:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:804:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk_execution_shadow.log:820:  "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/full_pipeline_stage_summary.json:3:    "run_dir": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/full_pipeline_stage_summary.json:47:    "run_dir": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/full_pipeline_stage_summary.json:109:    "run_dir": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/full_pipeline_stage_summary.json:189:    "run_dir": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_execution_shadow_20260425_151606_20260425_094828_207f7928",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:3:  "artifact_root": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:24:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:37:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:52:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:69:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:142:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:154:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:172:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:183:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:201:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:216:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:233:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:252:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:273:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:390:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:400:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:408:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f"
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:414:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:746:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:751:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy_risk.log:766:  "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_risk_20260425_151606_20260425_094741_91245a9f",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:3:  "artifact_root": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:24:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:37:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:52:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:125:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:137:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:154:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:165:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:182:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:197:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:214:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:233:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:342:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:352:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:360:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c"
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:366:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:689:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:694:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features_strategy.log:708:  "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_strategy_20260425_151606_20260425_094649_cad05b6c",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:3:  "artifact_root": "run/replay_audits/full_pipeline_after_csv_materialization_20260425_151606/replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:24:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:37:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:109:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:121:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:137:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:148:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:164:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:179:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:196:              "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:296:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:306:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:314:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde"
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:320:        "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:634:    "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:639:      "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/replay_full_pipeline_after_csv_materialization_20260425_151606/feeds_features.log:652:  "run_id": "replay_locked_single_day_full_pipeline_csv_feeds_features_20260425_151606_20260425_094608_0cf88dde",
run/proofs/B3_R31A_latest.json:29:    "write_candidate_audit_csv",
run/proofs/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738.json:7:  "latest_run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:13:    "a64_nested_run_dir": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:21:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/10_run_summary.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:26:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/engine_result.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:31:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/features_rows.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:36:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/risk_outputs.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:41:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/strategy_decisions.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:140:            "manifest_path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:141:            "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92"
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:152:            "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:243:              "manifest_path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:244:              "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92"
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:255:              "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:275:        "run_id": "replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:306:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:311:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/01_dataset_summary.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:316:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/02_scope_profile.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:321:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/03_integrity_report.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:326:        "path": "run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/04_metrics_summary.json",
run/proofs/proof_replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.json:330:    "run_summary_replay_scope": "feeds_features_strategy_risk",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2971:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2972:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2973:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2975:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2976:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2977:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2978:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2979:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2980:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2981:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2982:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2983:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2984:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2985:        "run/replay/replay_locked_single_day_phase_a4_true_owner_rerun_20260418_173649_9e3c2c88/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2994:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/features_rows.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2995:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/features_rows.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:2996:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/features_rows.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3001:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/artifacts/features_rows.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3002:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/artifacts/features_rows.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3016:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3018:          "run_id": "replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3031:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3033:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3034:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3036:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3037:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:3137:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/04_metrics_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4028:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4032:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4038:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4040:          "run_id": "replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4045:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4048:      "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4063:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4069:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4077:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4083:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4084:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4085:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4086:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/10_run_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4094:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4098:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4104:          "path": "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4106:          "run_id": "replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4111:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4114:      "path": "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4129:          "path": "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4135:          "path": "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4143:          "path": "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4149:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4150:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4151:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4152:        "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/10_run_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4160:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4164:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4170:          "path": "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4172:          "run_id": "replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4177:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4180:      "path": "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4195:          "path": "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4201:          "path": "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4209:          "path": "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4215:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4216:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4217:        "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4283:        "run/replay/replay_shadow_single_day_phasea1_shadow_true_cmp_20260418_131645_2ff6efb6/artifacts/10_run_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4291:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4295:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4301:          "path": "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4303:          "run_id": "replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4308:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4311:      "path": "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4326:          "path": "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4332:          "path": "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4340:          "path": "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4346:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4347:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4348:        "run/replay/replay_locked_single_day_scope_fix_check_5_20260418_105116_b2134953/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4356:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4360:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4366:          "path": "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4368:          "run_id": "replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4373:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4376:      "path": "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4391:          "path": "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4397:          "path": "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4405:          "path": "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4411:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4412:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4413:        "run/replay/replay_locked_single_day_features_truth_check_3_20260418_110038_6744942c/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4421:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4425:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4431:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4433:          "run_id": "replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4438:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4441:      "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4456:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4462:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4470:          "path": "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4476:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4477:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4478:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4479:        "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131110_7236fea5/artifacts/10_run_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4487:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4491:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4497:          "path": "run/replay/replay_locked_single_day_20260418_073935_16057e37/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4499:          "run_id": "replay_locked_single_day_20260418_073935_16057e37",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4504:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4507:      "path": "run/replay/replay_locked_single_day_20260418_073935_16057e37",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4522:          "path": "run/replay/replay_locked_single_day_20260418_073935_16057e37/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4528:          "path": "run/replay/replay_locked_single_day_20260418_073935_16057e37/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4536:          "path": "run/replay/replay_locked_single_day_20260418_073935_16057e37/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4542:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4543:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4544:        "run/replay/replay_locked_single_day_20260418_073935_16057e37/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4552:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4556:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4562:          "path": "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4564:          "run_id": "replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4569:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4572:      "path": "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4587:          "path": "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4593:          "path": "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4601:          "path": "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4607:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4608:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4609:        "run/replay/replay_locked_single_day_strategy_truth_check_20260418_110603_395e8ac3/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4617:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4621:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4627:          "path": "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4629:          "run_id": "replay_locked_single_day_features_truth_check_20260418_105533_db72751a",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4634:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4637:      "path": "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4652:          "path": "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4658:          "path": "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4666:          "path": "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4672:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4673:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4674:        "run/replay/replay_locked_single_day_features_truth_check_20260418_105533_db72751a/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4682:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4686:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4692:          "path": "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4694:          "run_id": "replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4699:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4702:      "path": "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4717:          "path": "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4723:          "path": "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4731:          "path": "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4737:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4738:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4739:        "run/replay/replay_locked_single_day_risk_truth_check_20260418_113513_c0ccb08c/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4747:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4751:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4757:          "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4759:          "run_id": "replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4764:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4767:      "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4782:          "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4788:          "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4796:          "path": "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4802:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4803:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4804:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4805:        "run/replay/replay_locked_single_day_phasea1_baseline_true_cmp_20260418_131703_062f77ac/artifacts/10_run_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4813:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4817:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4823:          "path": "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4825:          "run_id": "replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4830:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4833:      "path": "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4848:          "path": "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4854:          "path": "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4862:          "path": "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4868:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4869:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4870:        "run/replay/replay_locked_single_day_features_truth_check_2_20260418_105821_b4ea0744/01_dataset_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4878:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/artifacts/strategy_decisions.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4882:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/artifacts/features_rows.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4888:          "path": "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/00_manifest.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4890:          "run_id": "replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4895:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/00_manifest.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4898:      "path": "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4913:          "path": "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4920:          "path": "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/01_dataset_summary_economics_enriched_probe.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4926:          "path": "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4933:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/04_metrics_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4934:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/01_dataset_summary_economics_enriched_probe.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4935:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/03_integrity_report.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4936:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/01_dataset_summary.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4937:        "run/replay/replay_locked_single_day_phase_a4_feed_input_enrichment_v1_rerun_20260418_175617_5f502f3d/artifacts/10_run_summary.json"
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4954:      "run/replay/replay_locked_single_day_phasea1_features_check_20260418_131311_8f8617ae/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4955:      "run/replay/replay_locked_single_day_phasea3_economics_check_20260418_132232_a6215458/artifacts/strategy_decisions.json",
run/proofs/proof_batch30f_r8_post_clean_mapping_recheck_latest.json:4956:      "run/replay/replay_locked_single_day_risk_truth_propagation_check_20260418_113854_67efdf2a/art
## Runner contract
============================================================
FILE=bin/replay_run.py
exists=1
compile_rc=0
--- head ---
#!/usr/bin/env python3
"""
bin/replay_run.py

Freeze-grade operational CLI entrypoint for one replay run of the
MME-ScalpX Permanent Replay & Validation Framework.

This version upgrades the feeds stage from placeholder output to a real
dataset->clock->injector replay bridge, while keeping downstream stages
explicitly thin until their replay wiring is frozen.
"""

from __future__ import annotations
# BEGIN BATCH27C_REPLAY_SAFETY_FIREWALL
try:
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety
except ModuleNotFoundError:
    import pathlib as _batch27c_pathlib
    import sys as _batch27c_sys

    _batch27c_here = _batch27c_pathlib.Path(__file__).resolve()
    for _batch27c_parent in [_batch27c_here.parent, *_batch27c_here.parents]:
        if (_batch27c_parent / "app" / "mme_scalpx").exists():
            if str(_batch27c_parent) not in _batch27c_sys.path:
                _batch27c_sys.path.insert(0, str(_batch27c_parent))
            break
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety

assert_replay_module_static_safety(__file__)
# END BATCH27C_REPLAY_SAFETY_FIREWALL

from datetime import datetime, timezone
from collections.abc import MutableMapping

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.artifacts import ReplayArtifactsWriter
from app.mme_scalpx.replay.clock import ReplayClock, ReplayClockConfig
from app.mme_scalpx.replay.contracts import ProfilesSection
from app.mme_scalpx.replay.dataset import DatasetDiscoveryConfig, ReplayDatasetRepository
from app.mme_scalpx.replay.engine import ReplayEngine
from app.mme_scalpx.replay.fill_model import (
    ReplayFillModelConfig,
    ReplayFillModelFactory,
    ReplayFillRequest,
)
from app.mme_scalpx.replay.injector import (
    ReplayInjectionEvent,
    ReplayInjector,
)
from app.mme_scalpx.replay.integrity import (
    ReplayIntegrityEvaluator,
    placeholder_pass_check,
    integrity_bundle_to_dict,
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_REPRODUCIBILITY,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    ReplayIntegrityCheckResult,
    IntegrityVerdict,
)
from app.mme_scalpx.replay.modes import (
    DoctrineMode,
    ReplayScope,
    ReplaySideMode,
    ReplaySelectionMode,
    ReplaySpeedMode,
)
from app.mme_scalpx.replay.reports import build_report_bundle, report_bundle_to_dict
from app.mme_scalpx.replay.runner import ReplayRunConfig, ReplayRunner
from app.mme_scalpx.replay.selectors import (
    ReplaySelectionRequest,
    ReplaySelector,
    ReplayTimeWindow,
    selection_plan_to_dict,
)
from app.mme_scalpx.replay.topology import ReplayTopologyBuilder, topology_plan_to_dict


REQUIRED_CHECKS = (
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_REPRODUCIBILITY,
)


class ReplayRunCliError(RuntimeError):
    """CLI-layer replay run error."""






class LocalReplayTransport:
    """
    Replay-safe local transport used by this CLI phase.

    It does not publish to live/runtime infrastructure. It stores replay-safe
    publications locally so later stages can consume deterministic upstream
    outputs without contaminating live namespaces.
    """

    def __init__(self) -> None:
        self._published_requests: list[Any] = []
        self._feature_frames: list[dict[str, Any]] = []
        self._strategy_decisions: list[dict[str, Any]] = []
        self._risk_outputs: list[dict[str, Any]] = []
        self._execution_shadow_results: list[dict[str, Any]] = []

    @property
    def published_requests(self) -> tuple[Any, ...]:
        return tuple(self._published_requests)

    @property
    def feature_frames(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._feature_frames)

    @property
    def strategy_decisions(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._strategy_decisions)

    @property
    def risk_outputs(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._risk_outputs)

    @property
    def execution_shadow_results(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._execution_shadow_results)

    def publish(self, request) -> Mapping[str, Any] | None:
        self._published_requests.append(request)
        return {
            "published": True,
            "channel": request.event.channel,
            "sequence_id": request.event.sequence_id,
            "event_time": request.event.event_time,
        }

    def feed_requests(self, *, channel_prefix: str) -> tuple[Any, ...]:
        return tuple(
            request
            for request in self._published_requests
            if request.event.channel.startswith(channel_prefix)
        )

    def publish_feature_frame(self, frame: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(frame)
        self._feature_frames.append(stored)
        return {
            "published": True,
            "channel": stored.get("feature_channel"),
            "frame_id": stored.get("frame_id"),
            "event_time": stored.get("event_time"),
        }

    def publish_strategy_decision(self, decision: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(decision)
        self._strategy_decisions.append(stored)
        return {
            "published": True,
            "channel": stored.get("decision_channel"),
            "decision_id": stored.get("decision_id"),
            "event_time": stored.get("event_time"),
            "action": stored.get("action"),
        }

    def publish_risk_output(self, risk_output: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(risk_output)
        self._risk_outputs.append(stored)
        return {
            "published": True,
            "channel": stored.get("risk_channel"),
            "risk_id": stored.get("risk_id"),
            "event_time": stored.get("event_time"),
            "risk_action": stored.get("risk_action"),
            "veto_entry": stored.get("veto_entry"),
        }

    def publish_execution_shadow_result(
        self,
        execution_result: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        stored = dict(execution_result)
        self._execution_shadow_results.append(stored)
        return {
            "published": True,
            "channel": stored.get("execution_channel"),
            "execution_id": stored.get("execution_id"),
            "event_time": stored.get("event_time"),
            "filled": stored.get("filled"),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="replay_run.py",
        description="Run one frozen replay backbone execution.",
    )

    parser.add_argument("--dataset-root", required=True, help="Replay dataset root directory")
    parser.add_argument(
        "--selection-mode",
        required=True,
        choices=[mode.value for mode in ReplaySelectionMode],
        help="Canonical replay selection mode",
    )
============================================================
FILE=bin/replay_batch.py
exists=1
compile_rc=0
--- head ---
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.artifact_materializer import materialize_replay_run_artifacts  # noqa: E402
from app.mme_scalpx.replay.batch_runner import (  # noqa: E402
    build_date_list_plan,
    build_date_range_plan,
    build_intraday_window_plan,
    build_scenario_matrix_plan,
    build_single_day_plan,
    simulate_replay_batch_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay-only batch runner. Does not touch live Redis or brokers.")
    parser.add_argument("--scope", choices=["single_day", "date_range", "date_list", "intraday_window", "scenario_matrix"], required=True)
    parser.add_argument("--day")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--dates", nargs="*")
    parser.add_argument("--start-time")
    parser.add_argument("--end-time")
    parser.add_argument("--scenario")
    parser.add_argument("--out-root", default="run/replay")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.scope == "single_day":
        if not args.day:
            raise SystemExit("--day required for single_day")
        plan = build_single_day_plan(day=args.day, scenario_id=args.scenario)
    elif args.scope == "date_range":
        if not args.start_date or not args.end_date:
            raise SystemExit("--start-date and --end-date required for date_range")
        plan = build_date_range_plan(start_date=args.start_date, end_date=args.end_date, scenario_id=args.scenario)
    elif args.scope == "date_list":
        if not args.dates:
            raise SystemExit("--dates required for date_list")
        plan = build_date_list_plan(dates=tuple(args.dates), scenario_id=args.scenario)
    elif args.scope == "intraday_window":
        if not args.day or not args.start_time or not args.end_time:
            raise SystemExit("--day, --start-time, and --end-time required for intraday_window")
        plan = build_intraday_window_plan(day=args.day, start_time=args.start_time, end_time=args.end_time, scenario_id=args.scenario)
    else:
        if not args.dates:
            raise SystemExit("--dates required for scenario_matrix")
        plan = build_scenario_matrix_plan(dates=tuple(args.dates), start_time=args.start_time, end_time=args.end_time)

    result = simulate_replay_batch_plan(plan)
    payload = {
        "plan": plan,
        "simulation_result": result,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return 0

    materialized = materialize_replay_run_artifacts(
        run_id=str(plan["plan_id"]),
        plan=plan,
        simulation_result=result,
        base_dir=args.out_root,
    )
    print(json.dumps(materialized, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
============================================================
FILE=app/mme_scalpx/replay/runner.py
exists=1
compile_rc=0
--- head ---
"""
app/mme_scalpx/replay/runner.py

Freeze-grade replay run assembly layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Runner responsibilities
-----------------------
This module owns:
- replay run-id generation / validation
- replay run directory planning
- canonical artifact path planning
- selection-plan attachment
- manifest skeleton assembly
- doctrine-mode-aware manifest shaping
- top-level replay run context construction

This module does not own:
- replay clock driving
- dataset discovery internals
- selection policy internals
- replay injection
- topology execution
- experiment business logic
- metric/report computation
- live runtime mutation

Design rules
------------
- runner must be deterministic and auditable
- runner must not mutate dataset or selection truth
- manifest assembly must strictly respect contracts.py
- locked / shadow / differential separation must remain explicit
- artifact paths must be stable and reconstructible
- no doctrine logic belongs here
"""

from __future__ import annotations

# BEGIN BATCH27C_REPLAY_SAFETY_FIREWALL
try:
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety
except ModuleNotFoundError:
    import pathlib as _batch27c_pathlib
    import sys as _batch27c_sys

    _batch27c_here = _batch27c_pathlib.Path(__file__).resolve()
    for _batch27c_parent in [_batch27c_here.parent, *_batch27c_here.parents]:
        if (_batch27c_parent / "app" / "mme_scalpx").exists():
            if str(_batch27c_parent) not in _batch27c_sys.path:
                _batch27c_sys.path.insert(0, str(_batch27c_parent))
            break
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety

assert_replay_module_static_safety(__file__)
# END BATCH27C_REPLAY_SAFETY_FIREWALL

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

from .contracts import (
    ARTIFACT_BLOCKER_BREAKDOWN,
    ARTIFACT_CANDIDATE_AUDIT,
    ARTIFACT_DATASET_SUMMARY,
    ARTIFACT_DIFFERENTIAL_REPORT,
    ARTIFACT_EFFECTIVE_INPUTS_JSON,
    ARTIFACT_EFFECTIVE_OVERRIDES_FLAT_JSON,
    ARTIFACT_EXIT_BREAKDOWN,
    ARTIFACT_INTEGRITY_REPORT,
    ARTIFACT_MANIFEST,
    ARTIFACT_METRICS_SUMMARY,
    ARTIFACT_SCOPE_PROFILE,
    ARTIFACT_TRADE_LOG,
    ARTIFACTS_SUBDIR,
    LOGS_SUBDIR,
    REPLAY_CHAPTER_NAME,
    REPLAY_RUNS_DIRNAME,
    ArtifactsSection,
    DatasetSection,
    EffectiveInputsSnapshot,
    ExperimentSection,
    IntegritySection,
    ProfilesSection,
    ReplayRunManifest,
    ReplaySection,
    ResetSection,
    SelectionSection,
    SelectionWindow,
    effective_inputs_to_dict,
    row_to_dict,
    validate_manifest,
)
from .modes import (
    DoctrineMode,
    ExperimentFamily,
    IntegrityVerdict,
    ReplayScope,
    ReplaySelectionMode,
    ReplaySideMode,
    ReplaySpeedMode,
    ReplayVerdictTag,
)
from .selectors import ReplaySelectionPlan, selection_plan_to_dict


class ReplayRunnerError(RuntimeError):
    """Base exception for replay runner failures."""


class ReplayRunnerValidationError(ReplayRunnerError):
    """Raised when run assembly inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayRunConfig:
    """
    Immutable run-assembly input.
    """

    doctrine_mode: DoctrineMode
    replay_scope: ReplayScope = ReplayScope.FEEDS_ONLY
    speed_mode: ReplaySpeedMode = ReplaySpeedMode.ACCELERATED
    side_mode: ReplaySideMode = ReplaySideMode.MIRRORED_BOTH
    run_label: str | None = None
    code_revision: str | None = None
    dataset_id: str | None = None
    profiles: ProfilesSection = field(default_factory=ProfilesSection)
    experiment_family: ExperimentFamily | None = None
    baseline_ref: str | None = None
    override_pack_id: str | None = None
    shadow_label: str | None = None
    differential_pair_id: str | None = None
    reset_policy: str = "full_reset"
    integrity_required_checks: tuple[str, ...] = field(default_factory=tuple)
    integrity_verdict: IntegrityVerdict | None = None
    integrity_waivers: tuple[str, ...] = field(default_factory=tuple)
    fill_model: str | None = None
    run_root: str | Path | None = None
    created_at: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayArtifactPlan:
    """
    Stable artifact path plan for a run.
    """

    root_dir: str
    manifest_path: str
    log_dir: str
    artifacts_dir: str
    dataset_summary_path: str
    scope_profile_path: str
    integrity_report_path: str
    metrics_summary_path: str
    trade_log_path: str
    candidate_audit_path: str
    blocker_breakdown_path: str
    exit_breakdown_path: str
    differential_report_path: str
    effective_inputs_path: str
    effective_overrides_flat_path: str

    def report_paths_minimum(self) -> tuple[str, ...]:
        return (
            self.dataset_summary_path,
            self.scope_profile_path,
            self.integrity_report_path,
            self.metrics_summary_path,
            self.effective_inputs_path,
            self.effective_overrides_flat_path,
        )


@dataclass(frozen=True, slots=True)
class ReplayRunContext:
    """
    Canonical run-assembly output for downstream replay layers.
    """

    run_id: str
    created_at: str
    doctrine_mode: DoctrineMode
    selection_plan: ReplaySelectionPlan
    run_config: ReplayRunConfig
    artifact_plan: ReplayArtifactPlan
    manifest: ReplayRunManifest

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "doctrine_mode": self.doctrine_mode.value,
            "selection_plan": selection_plan_to_dict(self.selection_plan),
            "artifact_plan": artifact_plan_to_dict(self.artifact_plan),
            "manifest_validated": True,
        }


class ReplayRunner:
    """
    Freeze-grade replay run assembler.
    """

    def __init__(self, *, run_root: str | Path | None = None) -> None:
        self._run_root = Path(run_root or REPLAY_RUNS_DIRNAME).expanduser()

    @property
    def run_root(self) -> Path:
        return self._run_root

    def build_run_context(
        self,
        selection_plan: ReplaySelectionPlan,
        run_config: ReplayRunConfig,
    ) -> ReplayRunContext:
============================================================
FILE=app/mme_scalpx/replay/batch_runner.py
exists=1
compile_rc=0
--- head ---
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Mapping

from app.mme_scalpx.replay.execution_shadow import (
    replay_shadow_assumption_profile,
    simulate_replay_execution_shadow,
)
from app.mme_scalpx.replay.feature_adapter import build_replay_feature_payload
from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.risk_adapter import build_replay_risk_decision
from app.mme_scalpx.replay.scenarios import (
    REPLAY_REQUIRED_SCENARIOS,
    apply_replay_scenario_to_row,
    build_scenario_execution_assumption,
    scenario_risk_effects,
)
from app.mme_scalpx.replay.strategy_adapter import build_replay_strategy_decision_payload


REPLAY_BATCH_RUNNER_CONTRACT_VERSION = "replay_batch_runner_v1"

REPLAY_BATCH_SUPPORTED_RUN_SCOPES = (
    "single_day",
    "date_range",
    "date_list",
    "intraday_window",
    "scenario_matrix",
)

REPLAY_BATCH_REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "run_id",
    "scope",
    "date",
    "dates",
    "start_time",
    "end_time",
    "scenario_id",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)


@dataclass(frozen=True)
class ReplayRunRequest:
    schema_version: str
    run_id: str
    scope: str
    date: str | None
    dates: tuple[str, ...]
    start_time: str | None
    end_time: str | None
    scenario_id: str | None
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    broker_calls_allowed: bool = False
    live_redis_writes_allowed: bool = False
    production_doctrine_changed: bool = False


def _iso_date(value: str) -> str:
    return date.fromisoformat(str(value)).isoformat()


def _date_range(start_date: str, end_date: str) -> tuple[str, ...]:
    start = date.fromisoformat(str(start_date))
    end = date.fromisoformat(str(end_date))
    if end < start:
        raise ValueError("end_date must be >= start_date")
    out = []
    cur = start
    while cur <= end:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return tuple(out)


def deterministic_replay_batch_id(payload: Mapping[str, Any], *, prefix: str = "replay_batch") -> str:
    return f"{prefix}_{replay_fingerprint(payload)[:24]}"


def build_replay_run_request(
    *,
    scope: str,
    run_id: str,
    date_value: str | None = None,
    dates: tuple[str, ...] | list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    if scope not in REPLAY_BATCH_SUPPORTED_RUN_SCOPES:
        raise ValueError(f"unsupported replay batch scope: {scope}")
    normalized_dates = tuple(_iso_date(d) for d in (dates or ()))
    normalized_date = _iso_date(date_value) if date_value else (normalized_dates[0] if normalized_dates else None)
    req = ReplayRunRequest(
        schema_version=REPLAY_BATCH_RUNNER_CONTRACT_VERSION,
        run_id=str(run_id),
        scope=str(scope),
        date=normalized_date,
        dates=normalized_dates,
        start_time=str(start_time) if start_time else None,
        end_time=str(end_time) if end_time else None,
        scenario_id=str(scenario_id) if scenario_id else None,
    )
    return {
        "schema_version": req.schema_version,
        "run_id": req.run_id,
        "scope": req.scope,
        "date": req.date,
        "dates": req.dates,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "scenario_id": req.scenario_id,
        "paper_armed_approved": req.paper_armed_approved,
        "live_trading_approved": req.live_trading_approved,
        "execution_arming_created": req.execution_arming_created,
        "broker_calls_allowed": req.broker_calls_allowed,
        "live_redis_writes_allowed": req.live_redis_writes_allowed,
        "production_doctrine_changed": req.production_doctrine_changed,
    }


def build_single_day_plan(*, day: str, scenario_id: str | None = None) -> dict[str, Any]:
    seed = {"scope": "single_day", "day": _iso_date(day), "scenario_id": scenario_id}
    plan_id = deterministic_replay_batch_id(seed)
    request = build_replay_run_request(
        scope="single_day",
        run_id=f"{plan_id}_0",
        date_value=day,
        dates=(day,),
        scenario_id=scenario_id,
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="single_day", requests=(request,))


def build_date_range_plan(*, start_date: str, end_date: str, scenario_id: str | None = None) -> dict[str, Any]:
    dates = _date_range(start_date, end_date)
    seed = {"scope": "date_range", "dates": dates, "scenario_id": scenario_id}
    plan_id = deterministic_replay_batch_id(seed)
    requests = tuple(
        build_replay_run_request(
            scope="date_range",
            run_id=f"{plan_id}_{idx}",
            date_value=day,
            dates=dates,
            scenario_id=scenario_id,
        )
        for idx, day in enumerate(dates)
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="date_range", requests=requests)


def build_date_list_plan(*, dates: tuple[str, ...] | list[str], scenario_id: str | None = None) -> dict[str, Any]:
    normalized = tuple(_iso_date(day) for day in dates)
    seed = {"scope": "date_list", "dates": normalized, "scenario_id": scenario_id}
    plan_id = deterministic_replay_batch_id(seed)
    requests = tuple(
        build_replay_run_request(
            scope="date_list",
            run_id=f"{plan_id}_{idx}",
            date_value=day,
            dates=normalized,
            scenario_id=scenario_id,
        )
        for idx, day in enumerate(normalized)
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="date_list", requests=requests)


def build_intraday_window_plan(
    *,
    day: str,
    start_time: str,
    end_time: str,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    seed = {
        "scope": "intraday_window",
        "day": _iso_date(day),
        "start_time": start_time,
        "end_time": end_time,
        "scenario_id": scenario_id,
    }
    plan_id = deterministic_replay_batch_id(seed)
    request = build_replay_run_request(
        scope="intraday_window",
        run_id=f"{plan_id}_0",
        date_value=day,
        dates=(day,),
        start_time=start_time,
        end_time=end_time,
        scenario_id=scenario_id,
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="intraday_window", requests=(request,))


def build_scenario_matrix_plan(
    *,
    dates: tuple[str, ...] | list[str],
    scenarios: tuple[str, ...] | list[str] = REPLAY_REQUIRED_SCENARIOS,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, Any]:
    normalized_dates = tuple(_iso_date(day) for day in dates)
    normalized_scenarios = tuple(str(s) for s in scenarios)
    seed = {
        "scope": "scenario_matrix",
        "dates": normalized_dates,
        "scenarios": normalized_scenarios,
        "start_time": start_time,
        "end_time": end_time,
    }
    plan_id = deterministic_replay_batch_id(seed)
