# R35B_R4B_june12_feeds_features_shortpath_20260613_173242

classification: PASS_R35B_R4B_FEEDS_FEATURES_SHORTPATH_REPLAY_COMPLETED_NO_ORDER
proof: `run/proofs/R35B_R4B_june12_feeds_features_shortpath_20260613_173242.json`
dataset_root: `run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413`
run_root: `run/replay/r35b_r4b/20260613_173242`
replay_log: `run/audits/R35B_R4B_june12_feeds_features_shortpath_20260613_173242/replay.log`
inspect_json: `run/audits/R35B_R4B_june12_feeds_features_shortpath_20260613_173242/replay_inspect_summary.json`

## Safety
- PRE orders/risk/execution: 0 / 0 / 0
- POST orders/risk/execution: 0 / 0 / 0
- PRE risk/execution proc: 0 / 0
- POST risk/execution proc: 0 / 0

## RCs
- compile_rc: 0
- replay_rc: 0
- inspect_rc: 0

## Dataset shape
DATASET_ROOT=run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413
DAY=2026-06-12
RUN_ROOT=run/replay/r35b_r4b/20260613_173242

CSV row counts:
quote_ticks_mme_fut_stream.csv rows=16440
quote_ticks_mme_opt_stream.csv rows=79076

## Replay log tail
        ]
      },
      "feed_input_contract_version": "v1",
      "feed_input_declaration_source": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/replay_dataset_declaration.json",
      "feed_input_economics_evaluable": false,
      "feed_input_missing_enriched_fields": [
        "source_frame_id",
        "side",
        "selected_leg",
        "entry_mode",
        "tick_size",
        "target_ticks",
        "stop_ticks",
        "reward_ticks",
        "reward_cost_ratio",
        "economics_reason"
      ],
      "feed_input_source_mode": "quote_only_recorded",
      "invalid_days": 0,
      "notes": [],
      "observed_source_fields": [
        "ask",
        "bid",
        "day",
        "day_root",
        "dst_root",
        "files",
        "instrument_key",
        "instrument_token",
        "ltp",
        "provider_id",
        "schema",
        "source_id",
        "source_stream",
        "src_day_root",
        "symbol",
        "ts_event"
      ],
      "optional_file_stems": [],
      "paper_live_enabled": false,
      "replay_dataset_economics_comparison_ready": false,
      "replay_dataset_readiness_message": "dataset declaration not present",
      "replay_dataset_readiness_ok": null,
      "replay_dataset_readiness_status": "no_declaration",
      "required_file_stems": [
        "quote_ticks_mme_fut_stream",
        "quote_ticks_mme_opt_stream"
      ],
      "source_mode": "quote_only_recorded",
      "supported_scopes": [
        "feeds_only",
        "feeds_features",
        "feeds_features_strategy",
        "feeds_features_strategy_risk",
        "feeds_features_strategy_risk_execution_shadow"
      ],
      "supported_suffixes": [
        ".csv",
        ".json",
        ".jsonl"
      ],
      "total_days": 1,
      "total_files": 3,
      "total_size_bytes": 14195246,
      "trading_days": [
        "2026-06-12"
      ],
      "valid_days": 1
    },
    "intraday_window": {
      "end": null,
      "start": null
    },
    "market_tags": [],
    "selected_days": [
      {
        "coverage": {
          "optional_missing": [],
          "optional_present": [],
          "readable_files": 3,
          "required_missing": [],
          "required_present": [],
          "total_size_bytes": 14195246,
          "validity": "valid"
        },
        "date_str": "2026-06-12",
        "day_fingerprint": "cf58bc420ef76cb0b3442469c5ad19709e11d1c2d317e63509eca33a60659d4c",
        "day_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/LANE-X-R35B-R3B_BUILD_JUNE12_JSONL_TO_QUOTE_REPLAY_DATASET_NO_PATCH_NO_REPLAY_NO_ORDER_convert_june12_durable_jsonl_envelope_fields_to_quote_only_recorded_replay_csv_dataset_20260613_172413/2026-06-12",
        "files": [
          {
            "line_count": 16441,
            "modified_at_utc": "2026-06-13T11:54:14Z",
            "name": "quote_ticks_mme_fut_stream.csv",
            "relative_path": "quote_ticks_mme_fut_stream.csv",
            "row_count": 16440,
            "sha256": "84ebdfb4dae514e2532c1d89836d4225aea1f2f2e0eaf579ecb802b3204311b5",
            "size_bytes": 2285257,
            "stem": "quote_ticks_mme_fut_stream",
            "suffix": ".csv"
          },
          {
            "line_count": 79077,
            "modified_at_utc": "2026-06-13T11:54:17Z",
            "name": "quote_ticks_mme_opt_stream.csv",
            "relative_path": "quote_ticks_mme_opt_stream.csv",
            "row_count": 79076,
            "sha256": "98512058a1d91d6c49b43280db95652f16ca9c276170c5209ef22dfb56819b27",
            "size_bytes": 11907659,
            "stem": "quote_ticks_mme_opt_stream",
            "suffix": ".csv"
          },
          {
            "line_count": 35,
            "modified_at_utc": "2026-06-13T11:54:17Z",
            "name": "source_manifest.json",
            "relative_path": "source_manifest.json",
            "row_count": null,
            "sha256": "2f9379c114387da542e39879ac95a08c840561156baac017eebe45bf3031ae5a",
            "size_bytes": 2330,
            "stem": "source_manifest",
            "suffix": ".json"
          }
        ]
      }
    ],
    "selection_fingerprint": "141699083a79e32c2154caf4dce5a9129a71de4558c838da1790c43977ef46f7",
    "selection_mode": "single_day",
    "selection_notes": [],
    "session_segment": null,
    "trading_dates": [
      "2026-06-12"
    ]
  },
  "status": "ok",
  "topology_plan": {
    "notes": [],
    "scope": "feeds_features",
    "stage_names": [
      "feeds",
      "features"
    ],
    "stages": [
      {
        "description": "Replay input publication / feed-stage chain entry.",
        "order_index": 0,
        "owns_runtime_decisioning": false,
        "stage_name": "feeds",
        "terminal_stage": false
      },
      {
        "description": "Feature computation stage driven from replayed feed truth.",
        "order_index": 1,
        "owns_runtime_decisioning": true,
        "stage_name": "features",
        "terminal_stage": true
      }
    ],
    "topology_fingerprint": "420297be0e90c429b2008e3b0423f9329d7c96ea0250d92f96e58ff9d7d3de52"
  }
}

## Inspect summary
{
  "csv_counts": {
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/06_candidate_audit.csv": 0,
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/11_run_summary.csv": 1,
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/blocker_distribution.csv": 0,
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/family_side_summary.csv": 0
  },
  "exists": true,
  "file_count": 19,
  "files": [
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/00_manifest.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/02_scope_profile.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/04_metrics_summary.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/06_candidate_audit.csv",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/03_integrity_report.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/01_dataset_summary.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/17_effective_inputs.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/18_effective_overrides_flat.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/10_run_summary.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/b3_r32_analysis_exports_status.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/strategy_decisions.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/blocker_distribution.csv",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/risk_outputs.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/engine_result.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/features_rows.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/execution_shadow_results.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/economics_summary.json",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/11_run_summary.csv",
    "run/replay/r35b_r4b/20260613_173242/replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/family_side_summary.csv"
  ],
  "json_summaries": {
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/00_manifest.json": {
      "run_id": "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5"
    },
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/18_effective_overrides_flat.json": {
      "run_id": "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5"
    },
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/10_run_summary.json": {
      "feature_row_count": 95516,
      "run_id": "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5"
    },
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/b3_r32_analysis_exports_status.json": {
      "status": "ok"
    },
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/economics_summary.json": {
      "row_count": {
        "features_rows": 95516,
        "strategy_decisions": 0
      }
    },
    "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5/artifacts/engine_result.json": {
      "run_id": "replay_locked_single_day_r35b_r4b_june12_ff_20260613_120245_c62b6ec5"
    }
  },
  "run_root": "run/replay/r35b_r4b/20260613_173242"
}