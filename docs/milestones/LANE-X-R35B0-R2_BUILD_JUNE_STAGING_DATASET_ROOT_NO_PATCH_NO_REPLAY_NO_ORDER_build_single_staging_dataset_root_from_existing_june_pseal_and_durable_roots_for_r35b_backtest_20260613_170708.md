# LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708

classification: PASS_R35B0_R2_JUNE_STAGING_DATASET_ROOT_BUILT_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708.json`
stage_root: `run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708`
manifest: `run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/june_staging_manifest.json`

## Safety
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0

## Build result
- build_rc: 0
- usable_days: 2026-06-01,2026-06-02,2026-06-03,2026-06-04,2026-06-05,2026-06-08,2026-06-09,2026-06-11,2026-06-12
- weak_or_missing_days: 

## Manifest
{
  "day_count": 9,
  "days": {
    "2026-06-01": {
      "day": "2026-06-01",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 26663334,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 43806,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 25665019,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 427,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 1118709,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-01",
      "status": "STAGED_USABLE"
    },
    "2026-06-02": {
      "day": "2026-06-02",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 128336688,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 188,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 24200765,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 56797,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 291769,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-02",
      "status": "STAGED_USABLE"
    },
    "2026-06-03": {
      "day": "2026-06-03",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 21634131,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 191,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 1640165,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 8905,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 304294,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-03",
      "status": "STAGED_USABLE"
    },
    "2026-06-04": {
      "day": "2026-06-04",
      "exists": true,
      "files": {
        "SHA256SUMS.txt": {
          "mode": "symlink",
          "size": 1628,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/SHA256SUMS.txt",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/SHA256SUMS.txt"
        },
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 77794195,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 334065,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 9252847,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 24114,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 155118,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-04",
      "status": "STAGED_USABLE"
    },
    "2026-06-05": {
      "day": "2026-06-05",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 34948383,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 1767172,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 2811531,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 54779,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 19025,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-05",
      "status": "STAGED_USABLE"
    },
    "2026-06-08": {
      "day": "2026-06-08",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 90784726,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 126083,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 14722045,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 37992,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 242099,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260608_152347",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-08",
      "status": "STAGED_USABLE"
    },
    "2026-06-09": {
      "day": "2026-06-09",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 89640712,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 574,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 14307009,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 32408,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 386372,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260609_151625",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-09",
      "status": "STAGED_USABLE"
    },
    "2026-06-11": {
      "day": "2026-06-11",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 126437155,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 172926,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260611_152315",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-11",
      "status": "STAGED_USABLE"
    },
    "2026-06-12": {
      "day": "2026-06-12",
      "exists": true,
      "files": {
        "decisions.redisraw.gz": {
          "mode": "symlink",
          "size": 55237093,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/decisions.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/decisions.redisraw.gz"
        },
        "errors.redisraw.gz": {
          "mode": "symlink",
          "size": 112359,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/errors.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/errors.redisraw.gz"
        },
        "features.redisraw.gz": {
          "mode": "symlink",
          "size": 45532131,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/features.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/features.redisraw.gz"
        },
        "fut_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/fut_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/fut_dhan.redisraw.gz"
        },
        "fut_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/fut_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/fut_zerodha.redisraw.gz"
        },
        "opt_context_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_context_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/opt_context_dhan.redisraw.gz"
        },
        "opt_selected_dhan.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_selected_dhan.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/opt_selected_dhan.redisraw.gz"
        },
        "opt_selected_zerodha.redisraw.gz": {
          "mode": "symlink",
          "size": 21,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/opt_selected_zerodha.redisraw.gz",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/opt_selected_zerodha.redisraw.gz"
        },
        "pseal.log": {
          "mode": "symlink",
          "size": 1078,
          "source": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653/pseal.log",
          "staged": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12/pseal.log"
        }
      },
      "required_hit_count": 4,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260612_191653",
      "stage_day_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708/2026-06-12",
      "status": "STAGED_USABLE"
    }
  },
  "replay_note": "This stage root is index/manifest staging only. R35B replay must confirm runner accepts per-day subdirectories or use a builder adapter if needed.",
  "schema": "LANE-X-R35B0-R2 June staging dataset manifest",
  "stage_root": "run/staging/LANE-X-R35B0-R2_BUILD_JUNE_STAGING_DATASET_ROOT_NO_PATCH_NO_REPLAY_NO_ORDER_build_single_staging_dataset_root_from_existing_june_pseal_and_durable_roots_for_r35b_backtest_20260613_170708",
  "usable_days": [
    "2026-06-01",
    "2026-06-02",
    "2026-06-03",
    "2026-06-04",
    "2026-06-05",
    "2026-06-08",
    "2026-06-09",
    "2026-06-11",
    "2026-06-12"
  ],
  "weak_or_missing_days": []
}