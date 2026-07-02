# LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738
2026-06-07T13:57:38+05:30

LAW=OFFLINE_REPLAY_SMOKE_ONLY_NO_PATCH_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_BROKER_ORDER_NO_RISK_EXECUTION_START

DATASET_ROOT=run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337
RUN_ROOT=run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738
LOG=run/logs/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738_replay_run.log

## Preflight
REPLAY_RUN=FOUND
DATASET_MANIFEST=FOUND
DAY_MANIFEST=FOUND
FUT_TICKS=21808
OPT_TICKS=112227

## Running offline replay
REPLAY_RC=0

## Replay log tail
        "volume"
      ],
      "optional_file_stems": [],
      "replay_dataset_economics_comparison_ready": false,
      "replay_dataset_readiness_message": "dataset declaration not present",
      "replay_dataset_readiness_ok": null,
      "replay_dataset_readiness_status": "no_declaration",
      "required_file_stems": [],
      "supported_suffixes": [
        ".csv",
        ".json",
        ".jsonl"
      ],
      "total_days": 1,
      "total_files": 3,
      "total_size_bytes": 370924081,
      "trading_days": [
        "2026-06-02"
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
          "total_size_bytes": 370924081,
          "validity": "valid"
        },
        "date_str": "2026-06-02",
        "day_fingerprint": "4aebeccddcdcbd6a733c51d189e9b73572028e660d1c7cd92287642d26f47e13",
        "day_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/2026-06-02",
        "files": [
          {
            "line_count": 28,
            "modified_at_utc": "2026-06-02T16:54:07Z",
            "name": "dataset_manifest.json",
            "relative_path": "dataset_manifest.json",
            "row_count": null,
            "sha256": "af1700670fbd22b346a77cd96a4d99faa847e7ab56e62c6d83ae0011a309df74",
            "size_bytes": 1195,
            "stem": "dataset_manifest",
            "suffix": ".json"
          },
          {
            "line_count": 21808,
            "modified_at_utc": "2026-06-02T16:54:03Z",
            "name": "fut_ticks.jsonl",
            "relative_path": "fut_ticks.jsonl",
            "row_count": null,
            "sha256": "241d31d500471fd72b279992a88938b661d1f25e0e8e59002b3ca38e41406eb5",
            "size_bytes": 59600498,
            "stem": "fut_ticks",
            "suffix": ".jsonl"
          },
          {
            "line_count": 112227,
            "modified_at_utc": "2026-06-02T16:54:07Z",
            "name": "opt_ticks.jsonl",
            "relative_path": "opt_ticks.jsonl",
            "row_count": null,
            "sha256": "e9879eb6436b35346b5d16ec576bcc85668bb28e9b4e9c57f6b8022935c001cd",
            "size_bytes": 311322388,
            "stem": "opt_ticks",
            "suffix": ".jsonl"
          }
        ]
      }
    ],
    "selection_fingerprint": "8639cc6da9a861e893ad5a80bbeb73ec9c7fc78231a806192fa4d05920ef051f",
    "selection_mode": "single_day",
    "selection_notes": [],
    "session_segment": null,
    "trading_dates": [
      "2026-06-02"
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

## Output locator
LATEST_RUN_DIR=run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/00_manifest.json
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/04_metrics_summary.json
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/06_candidate_audit.csv
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/artifacts/10_run_summary.json
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/artifacts/features_rows.json
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/artifacts/strategy_decisions.json
FOUND run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b/artifacts/blocker_distribution.csv

## Artifact counts
CANDIDATE_AUDIT_LINES=134036
FEATURES_ROWS_BYTES=832600091
STRATEGY_DECISIONS_BYTES=253848028
BLOCKER_DISTRIBUTION_LINES=4

CLASSIFICATION=PASS_R2C_OFFLINE_REPLAY_SMOKE_OUTPUTS_CREATED
