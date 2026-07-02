# R27B MISB Shelf Width Scale / Window Audit

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_lines: 71250
redis_entries: 1250
valid_ltp_rows: 1250

## MISB active/default shelf thresholds
- DEFAULT_SHELF_WIDTH_MIN: 0.1
- DEFAULT_SHELF_WIDTH_MAX: 12.0

## Produced micro-shelf stats from Day-5 sealed futures
- source_counts: {'micro_shelf': 1250}
- shelf_snapshot_count_stats: {'n': 1250, 'min': 1.0, 'max': 65.0, 'mean': 47.4, 'median': 47.0, 'p75': 54.0, 'p90': 60.0, 'p95': 61.0}
- shelf_width_points_stats: {'n': 1248, 'min': 0.0, 'max': 42.70000000000073, 'mean': 12.957612179487237, 'median': 10.900000000001455, 'p75': 15.0, 'p90': 20.900000000001455, 'p95': 24.599999999998545}
- shelf_width_pct_stats: {'n': 1248, 'min': 0.0, 'max': 0.18221504362279664, 'mean': 0.0552651003423214, 'median': 0.046492681668027135, 'p75': 0.06394543323031014, 'p90': 0.08910129196873975, 'p95': 0.1048740871478023}
- current_width_proxy_valid_rows_count_min_0_10: 64

## Hypothetical shelf-width threshold hit counts
These are audit-only counts, not a threshold recommendation.
- width_pct >= 0.03: 984
- width_pct >= 0.05: 567
- width_pct >= 0.07: 264
- width_pct >= 0.075: 256
- width_pct >= 0.09: 124
- width_pct >= 0.1: 64

## Example rows
- {'stream_id': '1780651738536-0', 'ltp': 23446.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 3.0, 'width_points': 0.0, 'width_pct': 0.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 2.5}
- {'stream_id': '1780651740482-0', 'ltp': 23446.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 4.0, 'width_points': 0.0, 'width_pct': 0.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 2.9999999999999996}
- {'stream_id': '1780651741094-0', 'ltp': 23446.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 5.0, 'width_points': 0.0, 'width_pct': 0.0, 'delta_3': 0.0, 'velocity_ratio': 0.0, 'volume_norm': 3.333333333333333}
- {'stream_id': '1780651741718-0', 'ltp': 23455.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 6.0, 'width_points': 9.0, 'width_pct': 0.03837871260740709, 'delta_3': 9.0, 'velocity_ratio': 180.0, 'volume_norm': 3.571428571428571}
- {'stream_id': '1780651742194-0', 'ltp': 23455.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 7.0, 'width_points': 9.0, 'width_pct': 0.03837871260740709, 'delta_3': 9.0, 'velocity_ratio': 180.0, 'volume_norm': 3.571428571428571}
- {'stream_id': '1780651742435-0', 'ltp': 23463.9, 'shelf_source': 'micro_shelf', 'snapshot_count': 8.0, 'width_points': 17.900000000001455, 'width_pct': 0.07631651314541901, 'delta_3': 17.900000000001455, 'velocity_ratio': 358.0000000000291, 'volume_norm': 4.285714285714286}
- {'stream_id': '1780651743691-0', 'ltp': 23463.9, 'shelf_source': 'micro_shelf', 'snapshot_count': 9.0, 'width_points': 17.900000000001455, 'width_pct': 0.07631651314541901, 'delta_3': 17.900000000001455, 'velocity_ratio': 358.0000000000291, 'volume_norm': 3.888888888888889}
- {'stream_id': '1780651744927-0', 'ltp': 23464.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 10.0, 'width_points': 18.0, 'width_pct': 0.07674269878490728, 'delta_3': 9.0, 'velocity_ratio': 180.0, 'volume_norm': 4.0}
- {'stream_id': '1780651745445-0', 'ltp': 23461.8, 'shelf_source': 'micro_shelf', 'snapshot_count': 11.0, 'width_points': 18.0, 'width_pct': 0.07674269878490728, 'delta_3': -2.100000000002183, 'velocity_ratio': 42.000000000043656, 'volume_norm': 4.090909090909091}
- {'stream_id': '1780651746479-0', 'ltp': 23466.9, 'shelf_source': 'micro_shelf', 'snapshot_count': 12.0, 'width_points': 20.900000000001455, 'width_pct': 0.08910129196873975, 'delta_3': 3.0, 'velocity_ratio': 60.0, 'volume_norm': 4.166666666666667}
- {'stream_id': '1780651747206-0', 'ltp': 23466.9, 'shelf_source': 'micro_shelf', 'snapshot_count': 13.0, 'width_points': 20.900000000001455, 'width_pct': 0.08910129196873975, 'delta_3': 3.0, 'velocity_ratio': 60.0, 'volume_norm': 4.166666666666667}
- {'stream_id': '1780651747946-0', 'ltp': 23468.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 14.0, 'width_points': 22.0, 'width_pct': 0.09378863452274375, 'delta_3': 4.0, 'velocity_ratio': 80.0, 'volume_norm': 4.230769230769231}
- {'stream_id': '1780651748726-0', 'ltp': 23468.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 15.0, 'width_points': 22.0, 'width_pct': 0.09378863452274375, 'delta_3': 6.200000000000728, 'velocity_ratio': 124.00000000001455, 'volume_norm': 4.583333333333333}
- {'stream_id': '1780651748959-0', 'ltp': 23463.9, 'shelf_source': 'micro_shelf', 'snapshot_count': 16.0, 'width_points': 22.0, 'width_pct': 0.09378863452274375, 'delta_3': -3.0, 'velocity_ratio': 60.0, 'volume_norm': 5.0}
- {'stream_id': '1780651749432-0', 'ltp': 23469.0, 'shelf_source': 'micro_shelf', 'snapshot_count': 17.0, 'width_points': 23.0, 'width_pct': 0.09804966428647553, 'delta_3': 1.0, 'velocity_ratio': 20.0, 'volume_norm': 5.0}

## Interpretation
- This audit checks scale/window behavior only; it does not patch thresholds.
- R27A showed MISB mostly fails shelf_width_out_of_bounds.
- If Day-5 sealed micro-shelf width_pct remains mostly below 0.10, MISB shelf failure is a true width-boundary issue under the current window/min threshold.
- If width_pct is often above 0.10 here, then R10/R11/R25N were period-specific and Monday observe-only should decide.
- observed_max_width_pct: 0.18221504362279664
- observed_median_width_pct: 0.046492681668027135

R27B_MISB_SHELF_SCALE_WINDOW_AUDIT_OK=True