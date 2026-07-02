# LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249
2026-06-07T14:22:49+05:30

LAW=OFFLINE_RISK_EXECUTION_SHADOW_REPLAY_ONLY_NO_PATCH_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_BROKER_ORDER_NO_RISK_EXECUTION_START

DATASET_ROOT=run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337
RUN_ROOT=run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249
LOG=run/logs/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249_replay_run.log

## Preflight
R2F2=run/proofs/LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428.json
R3B=run/proofs/LANE-B-R3B_FILL_MODEL_ABI_AND_R4_COMMAND_CORRECTION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141930.json
REPLAY_RUN=FOUND
DATASET_MANIFEST=FOUND
DAY_MANIFEST=FOUND
FUT_TICKS=21808
OPT_TICKS=112227

## Running offline risk/execution-shadow replay
REPLAY_RC=0

## Replay log tail
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
    "scope": "feeds_features_strategy_risk_execution_shadow",
    "stage_names": [
      "feeds",
      "features",
      "strategy",
      "risk",
      "execution_shadow"
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
        "terminal_stage": false
      },
      {
        "description": "Risk gating stage applied to replay strategy outputs.",
        "order_index": 3,
        "owns_runtime_decisioning": true,
        "stage_name": "risk",
        "terminal_stage": false
      },
      {
        "description": "Replay-only execution shadow stage with no live side effects.",
        "order_index": 4,
        "owns_runtime_decisioning": true,
        "stage_name": "execution_shadow",
        "terminal_stage": true
      }
    ],
    "topology_fingerprint": "4b6fc95a56eb8cd691208a5c21bd70994aa136956bd1f683863f0090813eda59"
  }
}

## Output locator
LATEST_RUN_DIR=run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4

## Expected core artifacts
FOUND 6082 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/00_manifest.json
FOUND 59 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/04_metrics_summary.json
MISSING run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/05_trade_log.csv
FOUND 23152741 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/06_candidate_audit.csv
FOUND 2685 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/10_run_summary.json
FOUND 833538336 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/features_rows.json
FOUND 253848028 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/strategy_decisions.json
FOUND 226996266 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/risk_outputs.json
FOUND 96464774 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/execution_shadow_results.json
FOUND 740 bytes run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/blocker_distribution.csv

## Run summary PnL/shadow fields
replay_scope=feeds_features_strategy_risk_execution_shadow
candidate_count=0
trade_count=0
pnl_total=None
risk_row_count=134035
risk_vetoed_true_count=0
risk_action_breakdown={'HOLD': 134035}
execution_shadow_row_count=134035
execution_shadow_filled_count=0
execution_shadow_action_breakdown={}
strategy_action_breakdown={'HOLD': 134035}
feature_side_breakdown={'CALL': 56400, 'CONTEXT': 21808, 'PUT': 55827}
feature_leg_breakdown={'CALL_ATM': 56400, 'FUTURES': 21808, 'PUT_ATM': 55827}
integrity_verdict=pass

## Lightweight risk/execution-shadow artifact checks
--- run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/risk_outputs.json
BYTES=226996266
FIRST_300_BYTES:
[
  {
    "allowed": null,
    "blocker_name": "economics_fail",
    "blocker_name_fallback": "economics_fail",
    "blocker_reason": "hold_passthrough",
    "blocker_reason_fallback": "no_entry_condition",
    "candidate": false,
    "candidate_fallback": false,
    "decision_id": "strategy_decisio
LAST_300_BYTES:
sion_id": "strategy_decision_134035",
    "source_frame_id": "feature_frame_134035",
    "source_frame_id_fallback": "feature_frame_134035",
    "spread": 0.15000000000000568,
    "symbol": "NIFTY2660223350CE",
    "veto_entry": false,
    "veto_reason": "hold_passthrough",
    "vetoed": null
  }
]

--- run/replay/lane_b_r4/LANE-B-R4_A7_20260602_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_142249/replay_locked_single_day_lane-b-r4_a7_20260602_risk_execution_shadow_replay_smoke_no_patch_no_order_20260607_142249_20260607_085305_a66b56b4/artifacts/execution_shadow_results.json
BYTES=96464774
FIRST_300_BYTES:
[
  {
    "event_time": "2026-06-02T10:01:28Z",
    "execution_channel": "replay:execution_shadow",
    "execution_id": "execution_shadow_000001",
    "fill_price": null,
    "fill_qty": 0,
    "filled": false,
    "metadata": {
      "feature_truth_mode": "replay_bridge_v3_event_normalized",
      
LAST_300_BYTES:
cks",
      "symbol": "NIFTY2660223350CE",
      "trading_day": "2026-06-02",
      "ts_event": "2026-06-02T15:33:50Z"
    },
    "reason": "risk_block_or_non_entry",
    "risk_action": "HOLD",
    "slippage": null,
    "source_risk_id": "risk_output_134035",
    "symbol": "NIFTY2660223350CE"
  }
]


CLASSIFICATION=PASS_R4_RISK_EXECUTION_SHADOW_REPLAY_SMOKE_OUTPUTS_CREATED
