# B1-PROFIT-LIVE-R38ZK_directional_downmove_coverage_and_put_gate_sanity_audit_no_patch_no_order_20260531_231947

## Verdict
`CAPTURED_WINDOW_DID_NOT_INCLUDE_MAJOR_DAY_MOVE_ZERO_SIGNAL_PLAUSIBLE`

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``

## Result
- valid_projected_frames: `142`
- captured_change_points: `-37.099999999998545`
- captured_range_points: `67.80000000000291`
- audit_json: `run/tmp/B1-PROFIT-LIVE-R38ZK_directional_downmove_coverage_and_put_gate_sanity_audit_no_patch_no_order_20260531_231947_directional_gate_sanity.json`

## Meaning
This checks whether zero signal is plausible because the sealed capture missed the main downward move, or suspicious because PUT gates stayed zero despite captured movement.
