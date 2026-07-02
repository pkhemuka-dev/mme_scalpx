# LANE-B-R2E1_FINGERPRINT_PROVENANCE_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141109
2026-06-07T14:11:10+05:30

LAW=FINGERPRINT_AUDIT_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

{
  "artifact_shas": {
    "06_candidate_audit.csv": {
      "new": "699a37eb4d116ba9c5b7f29eadb214b7bfd497e81153aaff6f6ed2076d47d9bc",
      "old": "699a37eb4d116ba9c5b7f29eadb214b7bfd497e81153aaff6f6ed2076d47d9bc",
      "same": true
    },
    "artifacts/10_run_summary.json": {
      "new": "639ef2180f88474be83a18914241622af62f1f3529aaa9a5517441297d2870f4",
      "old": "3421f21030e138fcc69e0a947efb9a7bc1aa5ec55a8b56c30ce3f83f9c8450c1",
      "same": false
    },
    "artifacts/blocker_distribution.csv": {
      "new": "a23be5592b4da3ffb9a6c33d40b743544adca794c55607c6ddc01cd30c6a451d",
      "old": "a23be5592b4da3ffb9a6c33d40b743544adca794c55607c6ddc01cd30c6a451d",
      "same": true
    }
  },
  "dataset_file_shas": {
    "day_dataset_manifest": "af1700670fbd22b346a77cd96a4d99faa847e7ab56e62c6d83ae0011a309df74",
    "fut_ticks": "241d31d500471fd72b279992a88938b661d1f25e0e8e59002b3ca38e41406eb5",
    "opt_ticks": "e9879eb6436b35346b5d16ec576bcc85668bb28e9b4e9c57f6b8022935c001cd",
    "root_dataset_manifest": "af1700670fbd22b346a77cd96a4d99faa847e7ab56e62c6d83ae0011a309df74"
  },
  "fingerprint_diff_only": true,
  "new": {
    "manifest_dataset": {
      "coverage_summary": {
        "invalid_days": 0,
        "total_days": 1,
        "total_files": 3,
        "total_size_bytes": 370924081,
        "trading_days": [
          "2026-06-02"
        ],
        "valid_days": 1
      },
      "dataset_fingerprint": "e0b34ae189c9dd5ad105656df39bafa844386ed75370c4b45cd27471a77b71c6",
      "dataset_id": "B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
      "source_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337"
    },
    "manifest_profiles": {
      "batch_profile": null,
      "dataset_profile": null,
      "experiment_profile": null,
      "forensic_profile": null,
      "integrity_profile": null,
      "replay_profile": null
    },
    "manifest_replay": {
      "doctrine_mode": "locked",
      "fill_model": null,
      "scope": "feeds_features_strategy",
      "side_mode": "mirrored_both",
      "speed_mode": "accelerated"
    },
    "manifest_selection": {
      "market_tags": [],
      "selection_mode": "single_day",
      "session_segment": null,
      "trading_dates": [
        "2026-06-02"
      ],
      "window": {
        "end": null,
        "start": null
      }
    },
    "run_dir": "run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
    "run_id": "replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b",
    "summary_blocker_count": 134035,
    "summary_candidate_count": 0,
    "summary_dataset_fingerprint": "e0b34ae189c9dd5ad105656df39bafa844386ed75370c4b45cd27471a77b71c6",
    "summary_dataset_id": "B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
    "summary_feature_row_count": 134035,
    "summary_input_fingerprint": "8639cc6da9a861e893ad5a80bbeb73ec9c7fc78231a806192fa4d05920ef051f",
    "summary_strategy_row_count": 134035,
    "summary_trade_count": 0
  },
  "old": {
    "manifest_dataset": {
      "coverage_summary": {
        "invalid_days": 0,
        "total_days": 1,
        "total_files": 3,
        "total_size_bytes": 370924081,
        "trading_days": [
          "2026-06-02"
        ],
        "valid_days": 1
      },
      "dataset_fingerprint": "146146ec2700eaa772ee57a3fea700db3f2c865e014de6dbb87c981e377d856c",
      "dataset_id": "B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
      "source_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337"
    },
    "manifest_profiles": {
      "batch_profile": null,
      "dataset_profile": null,
      "experiment_profile": null,
      "forensic_profile": null,
      "integrity_profile": null,
      "replay_profile": null
    },
    "manifest_replay": {
      "doctrine_mode": "locked",
      "fill_model": null,
      "scope": "feeds_features_strategy",
      "side_mode": "mirrored_both",
      "speed_mode": "accelerated"
    },
    "manifest_selection": {
      "market_tags": [],
      "selection_mode": "single_day",
      "session_segment": null,
      "trading_dates": [
        "2026-06-02"
      ],
      "window": {
        "end": null,
        "start": null
      }
    },
    "run_dir": "run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7",
    "run_id": "replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7",
    "summary_blocker_count": 134035,
    "summary_candidate_count": 0,
    "summary_dataset_fingerprint": "146146ec2700eaa772ee57a3fea700db3f2c865e014de6dbb87c981e377d856c",
    "summary_dataset_id": "B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
    "summary_feature_row_count": 134035,
    "summary_input_fingerprint": "6e8c5748b935e4f9094c1219d5ef81f4dc020b357df5dd0a3e4085b53595cd8d",
    "summary_strategy_row_count": 134035,
    "summary_trade_count": 0
  }
}
AUDIT_RC=0

CLASSIFICATION=PASS_R2E1_DIFF_IS_FINGERPRINT_PROVENANCE_ONLY_OUTPUTS_REPRODUCED
