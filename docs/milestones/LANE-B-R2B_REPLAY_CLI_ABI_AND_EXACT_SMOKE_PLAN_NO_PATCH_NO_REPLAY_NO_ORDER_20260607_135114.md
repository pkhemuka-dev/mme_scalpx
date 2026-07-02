# LANE-B-R2B_REPLAY_CLI_ABI_AND_EXACT_SMOKE_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_135114
2026-06-07T13:51:14+05:30

LAW=CLI_ABI_AUDIT_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Fixed R2A selected dataset
DATASET_ROOT=run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337
DAY_DIR=run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02
PREV_RUN_DIR=run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7
DATASET_MANIFEST=FOUND
DAY_MANIFEST=FOUND
FUT_TICKS=21808
OPT_TICKS=112227

## replay_run.py help
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
HELP_RC=0

## replay_compare.py help
usage: replay_compare.py [-h] --profile PROFILE --shadow-override
                         SHADOW_OVERRIDE --baseline-frames BASELINE_FRAMES
                         --shadow-frames SHADOW_FRAMES --output-root
                         OUTPUT_ROOT [--baseline-run-dir BASELINE_RUN_DIR]
                         [--shadow-run-dir SHADOW_RUN_DIR]
                         [--comparison-id COMPARISON_ID]

Replay frame comparison CLI

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --shadow-override SHADOW_OVERRIDE
  --baseline-frames BASELINE_FRAMES
  --shadow-frames SHADOW_FRAMES
  --output-root OUTPUT_ROOT
  --baseline-run-dir BASELINE_RUN_DIR
  --shadow-run-dir SHADOW_RUN_DIR
  --comparison-id COMPARISON_ID
COMPARE_HELP_RC=0

## replay_run.py argument/parser clues
34:import argparse
207:def build_parser() -> argparse.ArgumentParser:
208:    parser = argparse.ArgumentParser(
213:    parser.add_argument("--dataset-root", required=True, help="Replay dataset root directory")
214:    parser.add_argument(
220:    parser.add_argument("--single-day", help="YYYY-MM-DD for single_day / intraday_window / session_segment")
221:    parser.add_argument("--start-date", help="YYYY-MM-DD for date_range")
222:    parser.add_argument("--end-date", help="YYYY-MM-DD for date_range")
223:    parser.add_argument("--custom-dates", help="Comma-separated YYYY-MM-DD list for custom_date_list")
224:    parser.add_argument("--weekdays", help="Comma-separated weekday integers 0..6 for weekday_batch")
225:    parser.add_argument("--months", help="Comma-separated month integers 1..12 for monthly_batch")
226:    parser.add_argument("--window-start", help="HH:MM[:SS] intraday window start")
227:    parser.add_argument("--window-end", help="HH:MM[:SS] intraday window end")
228:    parser.add_argument("--session-segment", help="Named session segment for session_segment mode")
229:    parser.add_argument(
235:    parser.add_argument(
241:    parser.add_argument(
247:    parser.add_argument("--run-label", default=None)
248:    parser.add_argument("--experiment-profile", default=None)
249:    parser.add_argument("--override-pack-id", default=None)
250:    parser.add_argument("--dataset-id", default=None)
251:    parser.add_argument("--fill-model", default=None)
252:    parser.add_argument("--run-root", default=None)
253:    parser.add_argument("--required-file-stems", default="")
254:    parser.add_argument("--optional-file-stems", default="")
255:    parser.add_argument("--supported-suffixes", default=".jsonl,.json,.csv")
256:    parser.add_argument("--recurse", action="store_true")
257:    parser.add_argument(
262:    parser.add_argument(
267:    parser.add_argument(
278:def parse_args(argv: list[str]) -> argparse.Namespace:
294:def build_selection_request(args: argparse.Namespace) -> ReplaySelectionRequest:
317:    - --dataset-root may point directly to a dataset directory containing YYYY-MM-DD day folders.
318:    - --dataset-root may also point to a parent directory when --dataset-id is supplied.
333:def build_dataset_repository(args: argparse.Namespace) -> ReplayDatasetRepository:
346:def build_run_config(args: argparse.Namespace) -> ReplayRunConfig:
2894:def main(argv: list[str]) -> int:
3091:    raise SystemExit(main(sys.argv[1:]))

## Previous R61D proof/log command clues
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:7:    "output_dir": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/date_range_aggregate",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:8:    "outputs": {
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:12:          "source_run_dir",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:29:          "source_run_dir",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:55:          "source_run_dir",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:73:          "source_run_dir",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:100:  "created_at_ist": "2026-06-02T22:28:09.527535+05:30",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:105:  "dataset_root": "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:106:  "day_dir": "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:126:  "next_route": "If PASS, run B3-R62 distinct-day aggregate comparison: 2026-05-27 + 2026-06-02. If BLOCKED, inspect replay log tail.",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:170:    "latest_run_dir": "run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7",
run/proofs/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337.json:182:  "session_date": "2026-06-02",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:7:    "output_dir": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/date_range_aggregate",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:8:    "outputs": {
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:12:          "source_run_dir",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:29:          "source_run_dir",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:55:          "source_run_dir",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:73:          "source_run_dir",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:100:  "created_at_ist": "2026-06-02T22:28:09.527535+05:30",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:105:  "dataset_root": "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:106:  "day_dir": "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:126:  "next_route": "If PASS, run B3-R62 distinct-day aggregate comparison: 2026-05-27 + 2026-06-02. If BLOCKED, inspect replay log tail.",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:170:    "latest_run_dir": "run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7",
run/audits/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_audit.json:182:  "session_date": "2026-06-02",
run/logs/B3-R61B_A7_DURABLE_CAPTURE_REPLAY_CONSUMABILITY_NO_REDIS_NO_PATCH_NO_ORDER_build_dataset_from_r61a_confirmed_durable_fut_opt_run_replay_exports_candidate_blocker_economics_audit_20260602_221650_replay_runner.log:13:  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3091, in <module>
run/logs/B3-R61B_A7_DURABLE_CAPTURE_REPLAY_CONSUMABILITY_NO_REDIS_NO_PATCH_NO_ORDER_build_dataset_from_r61a_confirmed_durable_fut_opt_run_replay_exports_candidate_blocker_economics_audit_20260602_221650_replay_runner.log:15:  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 2899, in main

## Existing previous run artifact quick check
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/00_manifest.json
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/04_metrics_summary.json
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/06_candidate_audit.csv
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/10_run_summary.json
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/features_rows.json
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/strategy_decisions.json
FOUND run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/blocker_distribution.csv

CLASSIFICATION=PASS_R2B_CLI_ABI_VISIBLE_READY_TO_WRITE_EXACT_R2C_OFFLINE_SMOKE_COMMAND
