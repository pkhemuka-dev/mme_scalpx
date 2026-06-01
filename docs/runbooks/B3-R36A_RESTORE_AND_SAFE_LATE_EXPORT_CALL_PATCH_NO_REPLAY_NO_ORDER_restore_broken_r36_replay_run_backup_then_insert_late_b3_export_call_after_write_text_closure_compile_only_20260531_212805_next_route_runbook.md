# B3-R36A_RESTORE_AND_SAFE_LATE_EXPORT_CALL_PATCH_NO_REPLAY_NO_ORDER next route

Run B3-R35 smoke test again.

Expected:

- replay_returncode=0
- integrity=pass
- status shows strategy_rows > 0 and features_rows > 0
- candidate_audit.csv exists
- blocker_distribution.csv rows > 0 or valid zero with candidate rows
- economics_summary.json has row counts
- family_side_summary.csv rows > 0
