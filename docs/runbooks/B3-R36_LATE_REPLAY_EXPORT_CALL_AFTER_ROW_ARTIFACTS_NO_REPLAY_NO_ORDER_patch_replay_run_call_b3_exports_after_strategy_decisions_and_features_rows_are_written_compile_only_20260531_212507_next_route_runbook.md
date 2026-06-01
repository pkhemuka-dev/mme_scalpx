# B3-R36_LATE_REPLAY_EXPORT_CALL_AFTER_ROW_ARTIFACTS_NO_REPLAY_NO_ORDER next route

Run B3-R35 smoke test again.

Expected:

- replay_returncode=0
- integrity=pass
- candidate_audit.csv or canonical candidate audit exists
- blocker_distribution.csv has rows
- economics_summary.json has row counts and selected_leg/economics_reason if present
- family_side_summary.csv has rows
- b3_r32_analysis_exports_status.json shows strategy_rows > 0 and features_rows > 0

If still blocked, inspect `b3_r36_late_export_error.json` and artifact paths.
