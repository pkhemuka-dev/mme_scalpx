# LANE-X-DASH-R4A_INTEGRATED_REPLAY_DASHBOARD_SOURCE_AUDIT_AND_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_source_and_replay_backtest_scripts_then_design_integrated_replay_dashboard_section_20260614_003858 runbook

## R4B recommended next step

Patch only:

`app/mme_scalpx/ops_dashboard/server.py`

Add:

- `replay_backtest_panel(params)`
- `latest_replay_runs()`
- `latest_replay_outputs()`
- GET form fields
- read-only tables
- no subprocess execution in R4B

## Later R4C/R4D

Add explicit offline-only execution using allowlisted commands after R4B is sealed.
