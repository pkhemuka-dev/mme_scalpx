# R35C_R4A_ENGINE_RESULT_INSPECT_NO_REPLAY_NO_ORDER_20260613_220834

classification: PASS_R35C_R4A_ENGINE_RESULT_INSPECT_DONE_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4A_ENGINE_RESULT_INSPECT_NO_REPLAY_NO_ORDER_20260613_220834.json`

safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## pointers
R4A_ROOT=run/replay/r35c_r4a/20260613_220130
RUN_DIR=run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8

## safety
orders=0 risk=0 execution=0

## key json files

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/00_manifest.json
{
  "artifacts": {
    "log_dir": "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/logs",
    "manifest_path": "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/00_manifest.json",
    "report_paths": [
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/01_dataset_summary.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/02_scope_profile.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/03_integrity_report.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/04_metrics_summary.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/17_effective_inputs.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/18_effective_overrides_flat.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/05_trade_log.csv",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/06_candidate_audit.csv",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/07_blocker_breakdown.json",
      "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/08_exit_breakdown.json"
    ],
    "root_dir": "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8"
  },
  "chapter": "replay",
  "code_revision": null,
  "created_at": "2026-06-13T16:31:39Z",
  "dataset": {
    "coverage_summary": {
      "invalid_days": 0,
      "total_days": 6,
      "total_files": 18,
      "total_size_bytes": 120337043,
      "trading_days": [
        "2026-06-01",
        "2026-06-02",
        "2026-06-03",
        "2026-06-04",
        "2026-06-05",
        "2026-06-12"
      ],
      "valid_days": 6
    },
    "dataset_fingerprint": "f55b89546c243e73677dc8ca2c7ba212ebf0f6e975cbe4b73698f79319958c87",
    "dataset_id": "r35c_r4a",
    "source_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset"
  },
  "experiment": {
    "baseline_ref": null,
    "differential_pair_id": null,
    "family": null,
    "override_pack_id": null,
    "shadow_label": null
  },
  "integrity": {
    "required_checks": [
      "heartbeat_integrity",
      "hash_freshness",
      "snapshot_sync_validity",
      "stale_leg_detection",
      "reset_cleanliness",
      "reproducibility_proof"
    ],
    "verdict": null,
    "waivers": []
  },
  "notes": [],
  "profiles": {
    "batch_profile": null,
    "dataset_profile": null,
    "experiment_profile": null,
    "forensic_profile": null,
    "integrity_profile": null,
    "replay_profile": null
  },
  "replay": {
    "doctrine_mode": "locked",
    "fill_model": null,
    "scope": "feeds_features_strategy_risk_execution_shadow",
    "side_mode": "mirrored_both",
    "speed_mode": "accelerated"
  },
  "reset": {
    "policy": "full_reset",
    "reset_completed_at": null,
    "reset_started_at": null,
    "reset_verdict": null
  },
  "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
  "selection": {
    "market_tags": [],
    "selection_mode": "single_day",
    "session_segment": null,
    "trading_dates": [
      "2026-06-01"
    ],
    "window": {
      "end": null,
      "start": null
    }
  },
  "verdict_tags": [
    "contractual_baseline"
  ]
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/01_dataset_summary.json
{
  "created_at_utc": "2026-06-13T16:31:39Z",
  "dataset_capability_consistency_message": "dataset declaration not present",
  "dataset_capability_consistency_ok": null,
  "dataset_capability_consistency_status": "no_declaration",
  "dataset_capability_profile": null,
  "dataset_capability_profile_path": null,
  "dataset_capability_profile_present": false,
  "dataset_declaration": null,
  "dataset_declaration_admissibility_message": "dataset declaration not present",
  "dataset_declaration_admissibility_ok": null,
  "dataset_declaration_admissibility_status": "no_declaration",
  "dataset_declaration_path": "etc/replay/datasets/replay_dataset_declaration_r35c_r4a_v1.json",
  "dataset_declaration_present": false,
  "dataset_fingerprint": "f55b89546c243e73677dc8ca2c7ba212ebf0f6e975cbe4b73698f79319958c87",
  "dataset_id": "r35c_r4a",
  "dataset_root": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset",
  "days": {
    "2026-06-01": {
      "day": "2026-06-01",
      "fut_missing": 0,
      "fut_rows": 21229,
      "opt_missing": 0,
      "opt_rows": 110139,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260601_100637/durable_capture"
    },
    "2026-06-02": {
      "day": "2026-06-02",
      "fut_missing": 0,
      "fut_rows": 21808,
      "opt_missing": 0,
      "opt_rows": 112227,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260602_100035/durable_capture"
    },
    "2026-06-03": {
      "day": "2026-06-03",
      "fut_missing": 0,
      "fut_rows": 9698,
      "opt_missing": 0,
      "opt_rows": 50261,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260603_101759/durable_capture"
    },
    "2026-06-04": {
      "day": "2026-06-04",
      "fut_missing": 0,
      "fut_rows": 18654,
      "opt_missing": 0,
      "opt_rows": 103192,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260604_093504/durable_capture"
    },
    "2026-06-05": {
      "day": "2026-06-05",
      "fut_missing": 0,
      "fut_rows": 18658,
      "opt_missing": 0,
      "opt_rows": 99424,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260605_091243/durable_capture"
    },
    "2026-06-12": {
      "day": "2026-06-12",
      "fut_missing": 0,
      "fut_rows": 16440,
      "opt_missing": 0,
      "opt_rows": 79076,
      "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture"
    }
  },
  "declared_capability_profile_id": null,
  "declared_capability_profile_version": null,
  "declared_profile_field_coverage_ok": null,
  "declared_profile_field_coverage_status": "no_profile_payload",
  "declared_profile_missing_required_fields": [],
  "declared_profile_required_fields": [],
  "declared_source_mode": null,
  "economics_eligible_for_evaluation": false,
  "economics_missing_required_fields": [
    "source_frame_id",
    "tick_size",
    "side",
    "selected_leg",
    "entry_mode",
    "target_ticks",
    "stop_ticks",
    "reward_ticks",
    "reward_cost_ratio",
    "economics_reason"
  ],
  "economics_source_mode": "recorded",
  "economics_source_status": "insufficient_source_truth",
  "economics_source_summary": {
    "candidate_context_fields_present": [],
    "effective_input_policy_fields_present": [],
    "eligible_for_economics_evaluation": false,
    "missing_required_fields": [
      "source_frame_id",
      "tick_size",
      "side",
      "selected_leg",
      "entry_mode",
      "target_ticks",
      "stop_ticks",
      "reward_ticks",
      "reward_cost_ratio",
      "economics_reason"
    ],
    "provenance_fields_present": [
      "economics_source_mode",
      "economics_source_status"
    ],
    "quote_cost_fields_present": [
      "ts_event",
      "symbol",
      "bid",
      "ask",
      "ltp"
    ],
    "recorded_policy_fields_present": [],
    "source_mode": "recorded",
    "source_status": "insufficient_source_truth"
  },
  "feed_input_contract": {
    "common_required_fields": [
      "ts_event",
      "symbol",
      "bid",
      "ask",
      "ltp"
    ],
    "contract_version": "v1",
    "economics_enriched_mode": {
      "economics_evaluable": true,
      "never_invent_fields": [
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
      "optional_fields": [],
      "required_fields": [
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
      "source_mode": "economics_enriched_recorded"
    },
    "never_invent_fields": [
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
    "optional_provenance_fields": [
      "source_file",
      "source_stem",
      "trading_day"
    ],
    "quote_only_mode": {
      "economics_evaluable": false,
      "never_invent_fields": [
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
      "optional_fields": [
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
      "required_fields": [],
      "source_mode": "quote_only_recorded"
    },
    "source_modes": [
      "quote_only_recorded",
      "economics_enriched_recorded"
    ]
  },
  "feed_input_contract_version": "v1",
  "feed_input_declaration_source": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/replay_dataset_declaration.json",
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
    "fut_missing",
    "fut_rows",
    "ltp",
    "opt_missing",
    "opt_rows",
    "source_file",
    "source_root",
    "symbol",
    "ts_event",
    "volume"
  ],
  "optional_file_stems": [],
  "replay_dataset_economics_comparison_ready": false,
  "replay_dataset_readiness_message": "dataset declaration not present",
  "replay_dataset_readiness_ok": null,
  "replay_dataset_readiness_status": "no_declaration",
  "required_file_stems": [],
  "schema_version": "r35c_r3a_quote_dataset_v1",
  "supported_suffixes": [
    ".csv",
    ".json",
    ".jsonl"
  ],
  "total_days": 6,
  "total_files": 18,
  "total_size_bytes": 120337043,
  "trading_days": [
    "2026-06-01",
    "2026-06-02",
    "2026-06-03",
    "2026-06-04",
    "2026-06-05",
    "2026-06-12"
  ],
  "valid_days": 6
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/02_scope_profile.json
{
  "selection_plan": {
    "dataset_summary": {
      "created_at_utc": "2026-06-13T16:31:39Z",
      "dataset_capability_consistency_message": "dataset declaration not present",
      "dataset_capability_consistency_ok": null,
      "dataset_capability_consistency_status": "no_declaration",
      "dataset_capability_profile": null,
      "dataset_capability_profile_path": null,
      "dataset_capability_profile_present": false,
      "dataset_declaration": null,
      "dataset_declaration_admissibility_message": "dataset declaration not present",
      "dataset_declaration_admissibility_ok": null,
      "dataset_declaration_admissibility_status": "no_declaration",
      "dataset_declaration_path": "etc/replay/datasets/replay_dataset_declaration_r35c_r4a_v1.json",
      "dataset_declaration_present": false,
      "dataset_fingerprint": "f55b89546c243e73677dc8ca2c7ba212ebf0f6e975cbe4b73698f79319958c87",
      "dataset_id": "r35c_r4a",
      "dataset_root": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset",
      "days": {
        "2026-06-01": {
          "day": "2026-06-01",
          "fut_missing": 0,
          "fut_rows": 21229,
          "opt_missing": 0,
          "opt_rows": 110139,
          "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260601_100637/durable_capture"
        },
        "2026-06-02": {
          "day": "2026-06-02",
          "fut_missing": 0,
          "fut_rows": 21808,
          "opt_missing": 0,
          "opt_rows": 112227,
          "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260602_100035/durable_capture"
        },
        "2026-06-03": {
          "day": "2026-06-03",
          "fut_missing": 0,
          "fut_rows": 9698,
          "opt_missing": 0,
          "opt_rows": 50261,
          "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260603_101759/durable_capture"
        },
        "2026-06-04": {
          "day": "2026-06-04",
          "fut_missing": 0,
          "fut_rows": 18654,
          "opt_missing": 0,
          "opt_rows": 103192,
          "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260604_093504/durable_capture"
        },
        "2026-06-05": {
          "day": "2026-06-05",
          "fut_missing": 0,
          "fut_rows": 18658,
          "opt_missing": 0,
          "opt_rows": 99424,
          "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260605_091243/durable_capture"
        },
        "2026-06-12": {
          "day": "2026-06-12",
          "fut_missing": 0,
          "fut_rows": 16440,
          "opt_missing": 0,
          "opt_rows": 79076,
          "source_root": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260612_093653/durable_capture"
        }
      },
      "declared_capability_profile_id": null,
      "declared_capability_profile_version": null,
      "declared_profile_field_coverage_ok": null,
      "declared_profile_field_coverage_status": "no_profile_payload",
      "declared_profile_missing_required_fields": [],
      "declared_profile_required_fields": [],
      "declared_source_mode": null,
      "economics_eligible_for_evaluation": false,
      "economics_missing_required_fields": [
        "source_frame_id",
        "tick_size",
        "side",
        "selected_leg",
        "entry_mode",
        "target_ticks",
        "stop_ticks",
        "reward_ticks",
        "reward_cost_ratio",
        "economics_reason"
      ],
      "economics_source_mode": "recorded",
      "economics_source_status": "insufficient_source_truth",
      "economics_source_summary": {
        "candidate_context_fields_present": [],
        "effective_input_policy_fields_present": [],
        "eligible_for_economics_evaluation": false,
        "missing_required_fields": [
          "source_frame_id",
          "tick_size",
          "side",
          "selected_leg",
          "entry_mode",
          "target_ticks",
          "stop_ticks",
          "reward_ticks",
          "reward_cost_ratio",
          "economics_reason"
        ],
        "provenance_fields_present": [
          "economics_source_mode",
          "economics_source_status"
        ],
        "quote_cost_fields_present": [
          "ts_event",
          "symbol",
          "bid",
          "ask",
          "ltp"
        ],
        "recorded_policy_fields_present": [],
        "source_mode": "recorded",
        "source_status": "insufficient_source_truth"
      },
      "feed_input_contract": {
        "common_required_fields": [
          "ts_event",
          "symbol",
          "bid",
          "ask",
          "ltp"
        ],
        "contract_version": "v1",
        "economics_enriched_mode": {
          "economics_evaluable": true,
          "never_invent_fields": [
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
          "optional_fields": [],
          "required_fields": [
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
          "source_mode": "economics_enriched_recorded"
        },
        "never_invent_fields": [
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
        "optional_provenance_fields": [
          "source_file",
          "source_stem",
          "trading_day"
        ],
        "quote_only_mode": {
          "economics_evaluable": false,
          "never_invent_fields": [
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
          "optional_fields": [
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
          "required_fields": [],
          "source_mode": "quote_only_recorded"
        },
        "source_modes": [
          "quote_only_recorded",
          "economics_enriched_recorded"
        ]
      },
      "feed_input_contract_version": "v1",
      "feed_input_declaration_source": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/replay_dataset_declaration.json",
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
        "fut_missing",
        "fut_rows",
        "ltp",
        "opt_missing",
        "opt_rows",
        "source_file",
        "source_root",
        "symbol",
        "ts_event",
        "volume"
      ],
      "optional_file_stems": [],
      "replay_dataset_economics_comparison_ready": false,
      "replay_dataset_readiness_message": "dataset declaration not present",
      "replay_dataset_readiness_ok": null,
      "replay_dataset_readiness_status": "no_declaration",
      "required_file_stems": [],
      "schema_version": "r35c_r3a_quote_dataset_v1",
      "supported_suffixes": [
        ".csv",
        ".json",
        ".jsonl"
      ],
      "total_days": 6,
      "total_files": 18,
      "total_size_bytes": 120337043,
      "trading_days": [
        "2026-06-01",
        "2026-06-02",
        "2026-06-03",
        "2026-06-04",
        "2026-06-05",
        "2026-06-12"
      ],
      "valid_days": 6
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
          "total_size_bytes": 23846525,
          "validity": "valid"
        },
        "date_str": "2026-06-01",
        "day_fingerprint": "553b72aabdfbe5f2ce5a3f8622a0c48bd807c620c27863887147db5f0069eefe",
        "day_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset/2026-06-01",
        "files": [
          {
            "line_count": 21230,
            "modified_at_utc": "2026-06-13T14:00:47Z",
            "name": "quote_ticks_mme_fut_stream.csv",
            "relative_path": "quote_ticks_mme_fut_stream.csv",
            "row_count": 21229,
            "sha256": "840c5f2fbd8719c7215043503b842fbbd82365f72b67f9030fd0312150f2c234",
            "size_bytes": 3736352,
            "stem": "quote_ticks_mme_fut_stream",
            "suffix": ".csv"
          },
          {
            "line_count": 110140,
            "modified_at_utc": "2026-06-13T14:00:50Z",
            "name": "quote_ticks_mme_opt_stream.csv",
            "relative_path": "quote_ticks_mme_opt_stream.csv",
            "row_count": 110139,
            "sha256": "d83b79bcc9acc15906cbc867b35ecd3f51bfe659cf2cf89b755f7adbaacf7342",
            "size_bytes": 20109951,
            "stem": "quote_ticks_mme_opt_stream",
            "suffix": ".csv"
          },
          {
            "line_count": 8,
            "modified_at_utc": "2026-06-13T14:00:50Z",
            "name": "source_manifest.json",
            "relative_path": "source_manifest.json",
            "row_count": null,
            "sha256": "05c948e473da0c6c115e01381f3d9a7f19c8df1e0c63ea4a7f70b076588b51d1",
            "size_bytes": 222,
            "stem": "source_manifest",
            "suffix": ".json"
          }
        ]
      }
    ],
    "selection_fingerprint": "43455114263bddc3d753768d49a004661b087163cf624563ba8479121196aaa2",
    "selection_mode": "single_day",
    "selection_notes": [],
    "session_segment": null,
    "trading_dates": [
      "2026-06-01"
    ]
  },
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

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/03_integrity_report.json
{
  "checks": [],
  "notes": [],
  "verdict": "fail"
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/04_metrics_summary.json
{
  "metrics": {
    "stage_count": 5
  },
  "notes": []
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/17_effective_inputs.json
{
  "dataset_input": {
    "coverage_summary": {
      "invalid_days": 0,
      "total_days": 6,
      "total_files": 18,
      "total_size_bytes": 120337043,
      "trading_days": [
        "2026-06-01",
        "2026-06-02",
        "2026-06-03",
        "2026-06-04",
        "2026-06-05",
        "2026-06-12"
      ],
      "valid_days": 6
    },
    "dataset_fingerprint": "f55b89546c243e73677dc8ca2c7ba212ebf0f6e975cbe4b73698f79319958c87",
    "dataset_id": "r35c_r4a",
    "intraday_window": {
      "end": null,
      "start": null
    },
    "selection_fingerprint": "43455114263bddc3d753768d49a004661b087163cf624563ba8479121196aaa2",
    "selection_mode": "single_day",
    "session_segment": null,
    "source_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/replay/staging/R35C_R3A_MATERIALIZE_DURABLE_JUNE_QUOTE_DATASETS_NO_REPLAY_NO_ORDER_20260613_193046_quote_dataset",
    "trading_dates": [
      "2026-06-01"
    ]
  },
  "experiment_input": {
    "baseline_ref": null,
    "differential_pair_id": null,
    "family": null,
    "override_pack_id": null,
    "profiles": {
      "batch_profile": null,
      "dataset_profile": null,
      "experiment_profile": null,
      "forensic_profile": null,
      "integrity_profile": null,
      "replay_profile": null
    },
    "shadow_label": null
  },
  "flattened_overrides": {
    "baseline_ref": null,
    "created_at": "2026-06-13T16:31:39Z",
    "differential_pair_id": null,
    "doctrine_mode": "locked",
    "notes": [],
    "override_pack_id": null,
    "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
    "shadow_label": null
  },
  "input_fingerprint": "43455114263bddc3d753768d49a004661b087163cf624563ba8479121196aaa2",
  "replay_profile_input": {
    "doctrine_mode": "locked",
    "fill_model": null,
    "integrity_required_checks": [
      "heartbeat_integrity",
      "hash_freshness",
      "snapshot_sync_validity",
      "stale_leg_detection",
      "reset_cleanliness",
      "reproducibility_proof"
    ],
    "integrity_waivers": [],
    "reset_policy": "full_reset",
    "scope": "feeds_features_strategy_risk_execution_shadow",
    "side_mode": "mirrored_both",
    "speed_mode": "accelerated"
  },
  "report_profile_input": {},
  "research_profile_input": {},
  "snapshot_created_at": "2026-06-13T16:31:39Z"
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/18_effective_overrides_flat.json
{
  "baseline_ref": null,
  "created_at": "2026-06-13T16:31:39Z",
  "differential_pair_id": null,
  "doctrine_mode": "locked",
  "notes": [],
  "override_pack_id": null,
  "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
  "shadow_label": null
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/engine_result.json
{
  "engine_finished_at": "2026-06-13T16:33:53Z",
  "engine_started_at": "2026-06-13T16:31:39Z",
  "final_state": "completed",
  "notes": [],
  "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
  "stage_count": 5,
  "stage_records": [
    {
      "finished_at": "2026-06-13T16:31:50Z",
      "order_index": 0,
      "output_summary": {
        "clock_after_stage": "2026-06-01T15:32:13Z",
        "day_breakdown": [
          {
            "injected_count": 131368,
            "last_sequence_id": 131368,
            "trading_day": "2026-06-01"
          }
        ],
        "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
        "stage_name": "feeds",
        "status": "ok",
        "total_injected": 131368
      },
      "stage_name": "feeds",
      "started_at": "2026-06-13T16:31:39Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:32:31Z",
      "order_index": 1,
      "output_summary": {
        "feature_channel": "replay:features",
        "feature_frames_published": 131368,
        "mode": "replay_feature_bridge",
        "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
        "source_feed_events": 131368,
        "stage_name": "features",
        "status": "ok"
      },
      "stage_name": "features",
      "started_at": "2026-06-13T16:31:50Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:33:49Z",
      "order_index": 2,
      "output_summary": {
        "action_breakdown": {
          "ENTRY": 4222,
          "HOLD": 127146
        },
        "decision_channel": "replay:decisions",
        "mode": "replay_strategy_bridge",
        "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
        "source_feature_frames": 131368,
        "stage_name": "strategy",
        "status": "ok",
        "strategy_decisions_published": 131368
      },
      "stage_name": "strategy",
      "started_at": "2026-06-13T16:32:31Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:33:51Z",
      "order_index": 3,
      "output_summary": {
        "mode": "replay_risk_bridge",
        "risk_action_breakdown": {
          "ENTER_CALL": 2033,
          "ENTER_PUT": 2189,
          "HOLD": 127146
        },
        "risk_channel": "replay:risk",
        "risk_outputs_published": 131368,
        "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
        "source_strategy_decisions": 131368,
        "stage_name": "risk",
        "status": "ok",
        "vetoed_entries": 0
      },
      "stage_name": "risk",
      "started_at": "2026-06-13T16:33:49Z",
      "success": true,
      "terminal_stage": false
    },
    {
      "finished_at": "2026-06-13T16:33:53Z",
      "order_index": 4,
      "output_summary": {
        "execution_channel": "replay:execution_shadow",
        "execution_results_published": 131368,
        "fill_model_name": "immediate_market",
        "filled_count": 4222,
        "mode": "replay_execution_shadow_bridge",
        "run_id": "replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8",
        "source_risk_outputs": 131368,
        "stage_name": "execution_shadow",
        "status": "ok"
      },
      "stage_name": "execution_shadow",
      "started_at": "2026-06-13T16:33:51Z",
      "success": true,
      "terminal_stage": true
    }
  ],
  "topology_summary": {
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

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/economics_summary.json
{
  "authority_candidates": {
    "stop_points": [
      {
        "line": 1212,
        "path": "app/mme_scalpx/core/models.py",
        "text": "_require_float(self.stop_points, \"stop_points\", min_value=0.0)",
        "value": 0.0
      },
      {
        "line": 154,
        "path": "app/mme_scalpx/services/features.py",
        "text": "DEFAULT_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 49,
        "path": "app/mme_scalpx/services/feature_family/miso_surface.py",
        "text": "DEFAULT_HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 50,
        "path": "app/mme_scalpx/services/feature_family/miso_surface.py",
        "text": "DEFAULT_DISASTER_STOP_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 80,
        "path": "app/mme_scalpx/services/strategy_family/misb.py",
        "text": "HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 81,
        "path": "app/mme_scalpx/services/strategy_family/misc.py",
        "text": "HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 81,
        "path": "app/mme_scalpx/services/strategy_family/misr.py",
        "text": "HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 81,
        "path": "app/mme_scalpx/services/strategy_family/mist.py",
        "text": "HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 81,
        "path": "app/mme_scalpx/services/strategy_family/miso.py",
        "text": "HARD_STOP_POINTS: Final[float] = 4.0",
        "value": 4.0
      },
      {
        "line": 141,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"proof_trade_shell states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
        "value": 5.0
      },
      {
        "line": 148,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Profit / Stop / Ratchet states TARGET_POINTS = 5.0 and HARD_STOP_POINTS = 4.0\",",
        "value": 5.0
      },
      {
        "line": 156,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Target, Stop, and Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
        "value": 5.0
      },
      {
        "line": 163,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Layer B / Target, Stop, Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
        "value": 5.0
      }
    ],
    "target_points": [
      {
        "line": 1232,
        "path": "app/mme_scalpx/core/models.py",
        "text": "_require_float(self.target_points, \"target_points\", min_value=0.0)",
        "value": 0.0
      },
      {
        "line": 153,
        "path": "app/mme_scalpx/services/features.py",
        "text": "DEFAULT_TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 48,
        "path": "app/mme_scalpx/services/feature_family/miso_surface.py",
        "text": "DEFAULT_TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 79,
        "path": "app/mme_scalpx/services/strategy_family/misb.py",
        "text": "TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 80,
        "path": "app/mme_scalpx/services/strategy_family/misc.py",
        "text": "TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 80,
        "path": "app/mme_scalpx/services/strategy_family/misr.py",
        "text": "TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 80,
        "path": "app/mme_scalpx/services/strategy_family/mist.py",
        "text": "TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 80,
        "path": "app/mme_scalpx/services/strategy_family/miso.py",
        "text": "TARGET_POINTS: Final[float] = 5.0",
        "value": 5.0
      },
      {
        "line": 141,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"proof_trade_shell states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
        "value": 5.0
      },
      {
        "line": 148,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Profit / Stop / Ratchet states TARGET_POINTS = 5.0 and HARD_STOP_POINTS = 4.0\",",
        "value": 5.0
      },
      {
        "line": 156,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Target, Stop, and Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
        "value": 5.0
      },
      {
        "line": 163,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Layer B / Target, Stop, Cooldown states TARGET_POINTS = 5 and HARD_STOP_POINTS = 4\",",
        "value": 5.0
      }
    ],
    "tick_size": [
      {
        "line": 953,
        "path": "app/mme_scalpx/core/models.py",
        "text": "tick_size: float = 0.0",
        "value": 0.0
      },
      {
        "line": 977,
        "path": "app/mme_scalpx/core/models.py",
        "text": "_require_float(self.tick_size, \"tick_size\", min_value=0.0)",
        "value": 0.0
      },
      {
        "line": 414,
        "path": "app/mme_scalpx/research_capture/normalizer.py",
        "text": "tick_size=float(_coerce_float(_first_present(ref, \"tick_size\", default=0.05), default=0.05)),",
        "value": 0.05
      },
      {
        "line": 81,
        "path": "app/mme_scalpx/services/strategy_family/misb.py",
        "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
        "value": 0.05
      },
      {
        "line": 82,
        "path": "app/mme_scalpx/services/strategy_family/misc.py",
        "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
        "value": 0.05
      },
      {
        "line": 82,
        "path": "app/mme_scalpx/services/strategy_family/misr.py",
        "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
        "value": 0.05
      },
      {
        "line": 82,
        "path": "app/mme_scalpx/services/strategy_family/mist.py",
        "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
        "value": 0.05
      },
      {
        "line": 460,
        "path": "app/mme_scalpx/services/strategy_family/doctrine_runtime.py",
        "text": "tick_size: float = 0.05",
        "value": 0.05
      },
      {
        "line": 82,
        "path": "app/mme_scalpx/services/strategy_family/miso.py",
        "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
        "value": 0.05
      },
      {
        "line": 155,
        "path": "etc/research_gate/raw_doctrine_economics_authority_map.json",
        "text": "\"Layer B states FUT_TICK_SIZE = 0.05\",",
        "value": 0.05
      }
    ]
  },
  "economics_reason_counts": {},
  "enriched_field_values": {
    "reward_cost_ratio": 1.25,
    "reward_points": 5.0,
    "reward_ticks": 100.0,
    "stop_points": 4.0,
    "stop_ticks": 80.0,
    "target_points": 5.0,
    "target_ticks": 100.0,
    "tick_size": 0.05
  },
  "enrichment_schema_version": "b3_r43_economics_export_enrichment_v1",
  "enrichment_sources": {
    "reward_cost_ratio": {
      "formula": "target_points / stop_points",
      "source_type": "derived_from_same_unit_basis",
      "stop_points": 4.0,
      "target_points": 5.0
    },
    "reward_points": {
      "basis": "reward for first target equals target_points in export summary",
      "source_type": "derived_same_as_target_points"
    },
    "reward_ticks": {
      "basis": "reward for first target equals target_ticks in export summary",
      "source_type": "derived_same_as_target_ticks"
    },
    "stop_points": {
      "line": 80,
      "path": "app/mme_scalpx/services/strategy_family/misb.py",
      "source_type": "source_assignment_candidate",
      "text": "HARD_STOP_POINTS: Final[float] = 4.0",
      "value": 4.0
    },
    "stop_ticks": {
      "formula": "stop_points / tick_size",
      "source_type": "derived_from_points_and_tick_size",
      "stop_points": 4.0,
      "tick_size": 0.05
    },
    "target_points": {
      "line": 79,
      "path": "app/mme_scalpx/services/strategy_family/misb.py",
      "source_type": "source_assignment_candidate",
      "text": "TARGET_POINTS: Final[float] = 5.0",
      "value": 5.0
    },
    "target_ticks": {
      "formula": "target_points / tick_size",
      "source_type": "derived_from_points_and_tick_size",
      "target_points": 5.0,
      "tick_size": 0.05
    },
    "tick_size": {
      "line": 81,
      "path": "app/mme_scalpx/services/strategy_family/misb.py",
      "source_type": "source_assignment_candidate",
      "text": "DEFAULT_TICK_SIZE: Final[float] = 0.05",
      "value": 0.05
    }
  },
  "enrichment_status": "enriched_source_labelled",
  "field_presence": {},
  "fields_left_missing": [
    "source_frame_id",
    "selected_leg",
    "entry_mode",
    "economics_reason"
  ],
  "governance_notes": [
    "Export-only enrichment; does not change strategy decisions.",
    "Values are source-labelled and must not be treated as trade/PnL proof.",
    "entry_mode=NO_ENTRY_HOLD_ONLY is only an export label when all rows are HOLD and candidate_true_count is zero.",
    "Do not claim paper/live, broker/order, risk/execution, or profitability readiness from this enrichment."
  ],
  "missing_economics_fields": [
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
  "note": "This is economics field completeness only; it is not PnL or trade profitability.",
  "row_count": {
    "features_rows": 0,
    "strategy_decisions": 0
  },
  "schema_version": "b3_r32_economics_summary_v1",
  "selected_leg_counts": {},
  "unit_basis": {
    "reward_points": "points",
    "reward_ticks": "derived_ticks_if_tick_size_available",
    "stop_points": "points",
    "stop_ticks": "derived_ticks_if_tick_size_available",
    "target_points": "points",
    "target_ticks": "derived_ticks_if_tick_size_available"
  },
  "value_counts": {}
}

### run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/b3_r32_analysis_exports_status.json
{
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
  "features_rows_path": "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/features_rows.json",
  "schema_version": "b3_r32_analysis_exports_status_v1",
  "status": "ok",
  "strategy_decisions_path": "run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/strategy_decisions.json",
  "strategy_rows": 0
}

## all files
12627 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/02_scope_profile.json
10361 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/economics_summary.json
7642 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/01_dataset_summary.json
5043 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/engine_result.json
3884 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/00_manifest.json
2336 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/17_effective_inputs.json
769 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/b3_r32_analysis_exports_status.json
278 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/18_effective_overrides_flat.json
202 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/06_candidate_audit.csv
113 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/blocker_distribution.csv
81 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/artifacts/family_side_summary.csv
59 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/04_metrics_summary.json
55 run/replay/r35c_r4a/20260613_220130/replay_locked_single_day_r35c_r4a_20260601_20260613_163139_aa8042f8/03_integrity_report.json
