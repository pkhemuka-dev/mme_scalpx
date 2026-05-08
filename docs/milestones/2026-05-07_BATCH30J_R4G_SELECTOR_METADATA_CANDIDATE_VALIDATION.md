# Batch 30J-R4G — Selector Metadata Candidate Validation

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: SELECTOR_METADATA_CANDIDATE_VALID_WITH_REVIEW_ITEMS

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Confirmed market-reference dates: [
  "2026-04-29"
]

Repair files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/00_selector_available_dates_candidate.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/01_replay_dataset_manifest_candidate.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/02_planned_replay_command_after_selector_validation.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/03_selector_metadata_candidate_readability_validation.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/04_30j_r4h_readiness.json"
]

Readability validation: {
  "available_dates": {
    "path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/00_selector_available_dates_candidate.json",
    "exists": true,
    "sha256": "53eb1decc51ad1f905371a205dbbdac2322ab895eb64fe71cb742ce83b5ff5e6",
    "json_ok": true,
    "keys": [
      "available_dates",
      "batch",
      "constraints",
      "dataset_id",
      "dataset_path",
      "generated_at_utc",
      "schema_version",
      "source",
      "status"
    ]
  },
  "manifest": {
    "path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/01_replay_dataset_manifest_candidate.json",
    "exists": true,
    "sha256": "1d2a21d7dd997d6c7709968a94d1aaf6872a86e565c1debeec845384836f8ad0",
    "json_ok": true,
    "keys": [
      "available_dates",
      "batch",
      "constraints",
      "dataset_id",
      "dataset_path",
      "generated_at_utc",
      "inventory_summary",
      "schema_version",
      "selection_support",
      "selector_source_summary",
      "status",
      "supported_suffixes"
    ]
  },
  "planned_command": {
    "path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/02_planned_replay_command_after_selector_validation.json",
    "exists": true,
    "sha256": "285c25e00129556409b1822b21ae7d307b7e9444e86303ebc467a8ff47b6d087",
    "json_ok": true,
    "keys": [
      "batch",
      "dataset_id",
      "dataset_parent",
      "doctrine_mode",
      "generated_at_utc",
      "may_execute_now",
      "next_required_before_execution",
      "run_root",
      "schema_version",
      "scope",
      "selected_dataset_path",
      "selection_mode",
      "single_day",
      "status"
    ]
  },
  "available_dates_field_valid": {
    "input": [
      "2026-04-29"
    ],
    "unique_sorted": [
      "2026-04-29"
    ],
    "invalid": [],
    "valid": true
  },
  "manifest_available_dates_field_valid": {
    "input": [
      "2026-04-29"
    ],
    "unique_sorted": [
      "2026-04-29"
    ],
    "invalid": [],
    "valid": true
  },
  "dates_match_expected": true,
  "planned_command_uses_confirmed_date": true,
  "planned_command_not_executed": true,
  "candidate_only_flags": true,
  "all_candidate_files_readable": true,
  "all_candidate_semantics_ok": true,
  "candidate_files": [
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/00_selector_available_dates_candidate.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/01_replay_dataset_manifest_candidate.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/02_planned_replay_command_after_selector_validation.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/03_selector_metadata_candidate_readability_validation.json",
    "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/04_30j_r4h_readiness.json"
  ],
  "repair_dir": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g"
}

Blockers: []

Review: [
  "ONLY_ONE_CONFIRMED_MARKET_REFERENCE_DATE_AVAILABLE_FOR_SELECTOR_METADATA"
]

Next: Review 30J-R4G warnings, then run 30J-R4H non-mutating selector readability probe; no replay execution.

Safety: candidate metadata only; no selector metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
