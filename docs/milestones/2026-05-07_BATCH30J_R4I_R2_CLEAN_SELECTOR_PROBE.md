# Batch 30J-R4I-R2 — Clean Source-Specific Selector API Probe

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: SELECTOR_API_ACCEPTED_CANDIDATE_DATE_WITH_REVIEW_ITEMS

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Accepted method: ReplaySelector._resolve_dates

Selector probe: {
  "imports": {
    "app.mme_scalpx.replay.selectors": {
      "ok": true,
      "file": "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/selectors.py"
    }
  },
  "steps": [
    {
      "name": "_validate_date_str",
      "ok": true,
      "date": "2026-04-29"
    },
    {
      "name": "ReplaySelectionMode",
      "ok": true,
      "mode_repr": "<ReplaySelectionMode.SINGLE_DAY: 'single_day'>",
      "mode_value": "single_day"
    },
    {
      "name": "ReplaySelectionRequest",
      "ok": true,
      "signature": "(selection_mode: 'ReplaySelectionMode', single_day: 'str | None' = None, start_date: 'str | None' = None, end_date: 'str | None' = None, custom_dates: 'tuple[str, ...]' = <factory>, intraday_window: 'ReplayTimeWindow' = <factory>, session_segment: 'str | None' = None, weekdays: 'tuple[int, ...]' = <factory>, months: 'tuple[int, ...]' = <factory>, market_tags: 'tuple[str, ...]' = <factory>) -> None",
      "request_repr": "ReplaySelectionRequest(selection_mode=<ReplaySelectionMode.SINGLE_DAY: 'single_day'>, single_day='2026-04-29', start_date=None, end_date=None, custom_dates=(), intraday_window=ReplayTimeWindow(start=None, end=None), session_segment=None, weekdays=(), months=(), market_tags=())"
    },
    {
      "name": "_validate_request",
      "ok": true
    },
    {
      "name": "ReplaySelector._resolve_dates",
      "ok": true,
      "result_type": "tuple",
      "result_repr": "('2026-04-29',)",
      "contains_day": true
    },
    {
      "name": "build_selection_plan_dummy_repository",
      "ok": false,
      "error": "AttributeError(\"'DummyRepository' object has no attribute 'build_dataset_summary'\")"
    }
  ],
  "accepted": true,
  "accepted_method": "ReplaySelector._resolve_dates",
  "selection_plan_dict": null,
  "step_ok_count": 5,
  "step_fail_count": 1
}

Probe files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/09_clean_source_specific_selector_api_probe.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/10_30j_r4j_readiness.json"
]

Blockers: []

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_REVIEW"
]

Next: Review one-date warning, then run 30J-R4J reversible metadata install plan + dry CLI selector validation only; no replay execution.

Safety: no metadata install, no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
