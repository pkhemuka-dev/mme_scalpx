# B1-PROFIT-LIVE-R38ZL_capture_grade_eligibility_and_partial_capture_root_cause_audit_no_patch_no_order_20260531_232815

## Verdict
`FORENSIC_ONLY_NOT_BACKTEST_GRADE`

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_feeds: ``
- lock_execution: ``

## Capture coverage
- futures_records: `218`
- option_records: `801`
- features_records: `446`
- decisions_records: `998`
- futures_span_minutes: `9.090566690133333`
- captured_net_change_points: `-37.099999999998545`
- captured_range_points: `67.80000000000291`
- futures_first_ist: `2026-05-29T15:20:50.204343+05:30`
- futures_last_ist: `2026-05-29T15:29:55.638345+05:30`

## Eligibility gates
- stream_files_present: `True`
- full_session_span: `False`
- useful_intraday_span: `False`
- tick_density_basic: `False`
- feature_decision_density_basic: `False`
- move_coverage_basic: `False`
- classic_data_valid_evidence: `True`
- candidate_lifecycle_present: `False`
- shadow_trade_lifecycle_present: `False`

## Failed gates
`['full_session_span', 'useful_intraday_span', 'tick_density_basic', 'feature_decision_density_basic', 'move_coverage_basic', 'candidate_lifecycle_present', 'shadow_trade_lifecycle_present']`

## Root causes
`['capture_window_too_short', 'tick_density_too_low', 'major_day_move_not_covered', 'feature_validity_repaired_but_no_candidate_lifecycle', 'not_full_session_capture']`

## Why partial
`['supervisor_detected_stale_feed_and_started_or_restarted_feeds_late', 'latest_supervisor_state_ts_utc=2026-05-29T10:15:48.882589+00:00', 'sealed_futures_span_only_9.09_minutes', 'sealed_futures_range_only_67.80_points', 'features_or_decisions_count_below_backtest_grade_threshold']`

## Conclusion
This dataset is useful for forensic debugging, but it is not backtest-grade unless the gates above pass.

## Tomorrow acceptance
- Full/long live observe-only window, not a small slice.
- Fresh futures + selected option through the window.
- Feature validity true in runtime.
- Candidate/blocker lifecycle visible.
- Shadow trade/PnL lifecycle before profitability conclusion.
