# R35B_R4H_strategy_skip_b3r32_20260613_180821

classification: PASS_R35B_R4H_STRATEGY_REPLAY_COMPLETED_B3R32_SKIPPED_NO_ORDER
proof: `run/proofs/R35B_R4H_strategy_skip_b3r32_20260613_180821.json`
run_root: `run/replay/r35b_r4h/20260613_180821`
log: `run/audits/R35B_R4H_strategy_skip_b3r32_20260613_180821/replay.log`
inspect: `run/audits/R35B_R4H_strategy_skip_b3r32_20260613_180821/inspect.json`

compile_rc=0 replay_rc=0 inspect_rc=0
safety pre=0/0/0 post=0/0/0 proc=0/0

## Replay log tail
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
    "selection_fingerprint": "744444159ef62e17423087dddc9da6ed6d47ba7ee146476bc9f2b33c1d000016",
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
    "scope": "feeds_features_strategy",
    "stage_names": [
      "feeds",
      "features",
      "strategy"
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
        "terminal_stage": false
      },
      {
        "description": "Strategy decision stage driven from replay feature truth.",
        "order_index": 2,
        "owns_runtime_decisioning": true,
        "stage_name": "strategy",
        "terminal_stage": true
      }
    ],
    "topology_fingerprint": "713b022a3596921add3ee5929103e03c7ed31031ad82eb06578e69fe4411a4a3"
  }
}

## Inspect
{
  "b3r32_status": {
    "blocker_distribution_rows": 0,
    "candidate_audit_rows": 0,
    "economics_missing_fields": [
      "source_frame_id",
      "selected_leg",
      "entry_mode",
      "tick_size",
      "target_ticks",
      "stop_ticks",
      "reward_ticks",
      "reward_cost_ratio",
      "economics_reason"
    ],
    "family_side_summary_rows": 0,
    "features_rows": 0,
    "features_rows_path": "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/features_rows.json",
    "schema_version": "b3_r32_analysis_exports_status_v1",
    "status": "ok",
    "strategy_decisions_path": "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/strategy_decisions.json",
    "strategy_rows": 0
  },
  "candidate_audit_rows": 0,
  "csv_counts": {
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/06_candidate_audit.csv": 0,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/11_run_summary.csv": 1,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/blocker_distribution.csv": 0,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/family_side_summary.csv": 0
  },
  "features_rows_size": 1072312817,
  "file_count": 19,
  "files": [
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/00_manifest.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/02_scope_profile.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/04_metrics_summary.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/06_candidate_audit.csv",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/03_integrity_report.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/01_dataset_summary.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/17_effective_inputs.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/18_effective_overrides_flat.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/10_run_summary.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/b3_r32_analysis_exports_status.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/strategy_decisions.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/blocker_distribution.csv",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/risk_outputs.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/engine_result.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/features_rows.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/execution_shadow_results.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/economics_summary.json",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/11_run_summary.csv",
    "run/replay/r35b_r4h/20260613_180821/replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/family_side_summary.csv"
  ],
  "json_sizes": {
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/00_manifest.json": 3716,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/01_dataset_summary.json": 6543,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/02_scope_profile.json": 10932,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/03_integrity_report.json": 7748,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/04_metrics_summary.json": 59,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/17_effective_inputs.json": 2285,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/18_effective_overrides_flat.json": 269,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/10_run_summary.json": 2332,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/b3_r32_analysis_exports_status.json": 751,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/economics_summary.json": 10361,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/engine_result.json": 3079,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/execution_shadow_results.json": 3,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/features_rows.json": 1072312817,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/risk_outputs.json": 3,
    "replay_locked_single_day_r35b_r4h_20260613_123824_5a5d5514/artifacts/strategy_decisions.json": 2566314450
  },
  "run_root": "run/replay/r35b_r4h/20260613_180821",
  "strategy_decisions_size": 2566314450
}