# Batch 30J-R4I — Source-Specific Selector Probe

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: SOURCE_SPECIFIC_SELECTOR_PROBE_BLOCKED

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Adapter validation: {
  "available_dates": [
    "2026-04-29"
  ],
  "selector_import_ok": true,
  "dataset_import_ok": true,
  "contracts_import_ok": true,
  "selector_functions": [
    {
      "name": "build_selection_plan",
      "lineno": 303,
      "args": [
        "repository",
        "request"
      ]
    },
    {
      "name": "selection_plan_to_dict",
      "lineno": 321,
      "args": [
        "plan"
      ]
    },
    {
      "name": "_validate_request",
      "lineno": 338,
      "args": [
        "request",
        "session_segments"
      ]
    },
    {
      "name": "_require_only",
      "lineno": 464,
      "args": [
        "request"
      ]
    },
    {
      "name": "_forbid_fields",
      "lineno": 513,
      "args": [
        "request"
      ]
    },
    {
      "name": "_validate_intraday_window",
      "lineno": 549,
      "args": [
        "window"
      ]
    },
    {
      "name": "_normalize_session_segments",
      "lineno": 565,
      "args": [
        "session_segments"
      ]
    },
    {
      "name": "_validate_market_tags",
      "lineno": 583,
      "args": [
        "market_tags"
      ]
    },
    {
      "name": "_validate_weekdays",
      "lineno": 591,
      "args": [
        "weekdays"
      ]
    },
    {
      "name": "_validate_months",
      "lineno": 599,
      "args": [
        "months"
      ]
    },
    {
      "name": "_validate_date_str",
      "lineno": 607,
      "args": [
        "date_str"
      ]
    },
    {
      "name": "_parse_time_str",
      "lineno": 620,
      "args": [
        "value"
      ]
    },
    {
      "name": "_date_to_weekday",
      "lineno": 629,
      "args": [
        "date_str"
      ]
    },
    {
      "name": "_date_to_month",
      "lineno": 633,
      "args": [
        "date_str"
      ]
    },
    {
      "name": "_stable_sha256_json",
      "lineno": 637,
      "args": [
        "value"
      ]
    },
    {
      "name": "__init__",
      "lineno": 130,
      "args": [
        "self",
        "repository"
      ]
    },
    {
      "name": "repository",
      "lineno": 142,
      "args": [
        "self"
      ]
    },
    {
      "name": "session_segments",
      "lineno": 146,
      "args": [
        "self"
      ]
    },
    {
      "name": "build_plan",
      "lineno": 149,
      "args": [
        "self",
        "request"
      ]
    },
    {
      "name": "_resolve_dates",
      "lineno": 196,
      "args": [
        "self",
        "request",
        "available_dates"
      ]
    },
    {
      "name": "_resolve_window_and_segment",
      "lineno": 281,
      "args": [
        "self",
        "request"
      ]
    }
  ],
  "selector_classes": [
    {
      "name": "ReplaySelectionError",
      "lineno": 53
    },
    {
      "name": "ReplaySelectionValidationError",
      "lineno": 57
    },
    {
      "name": "ReplaySelectionUnavailableError",
      "lineno": 61
    },
    {
      "name": "ReplayTimeWindow",
      "lineno": 83
    },
    {
      "name": "ReplaySelectionRequest",
      "lineno": 91
    },
    {
      "name": "ReplaySelectionPlan",
      "lineno": 109
    },
    {
      "name": "ReplaySelector",
      "lineno": 125
    }
  ],
  "selector_available_dates_context_seen": true,
  "dynamic_candidate_count": 43,
  "dynamic_attempt_count": 172,
  "dynamic_acceptance": false,
  "likely_issue_if_no_acceptance": "No safe selector callable matched generic probe signature; source-specific CLI/selector adapter validation needed.",
  "candidate_metadata_valid_for_date": true,
  "dataset_path": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0"
}

Dynamic accepted: False

Probe files: []

Blockers: [
  "ALL_RUNTIME_LOCKS_ABSENT_NOW_BLOCKER",
  "RUNTIME_PIDS_ABSENT_NOW_BLOCKER",
  "GENERIC_ABSENT_NOW_BLOCKER"
]

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_REVIEW",
  "DYNAMIC_SELECTOR_CALLABLE_ACCEPTANCE_STILL_NOT_PROVEN_SOURCE_CONTEXT_OK"
]

Next: Do not install metadata or run replay. Resolve 30J-R4I blockers first.

Safety: no metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
