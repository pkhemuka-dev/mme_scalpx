# R27C MISB Shelf Threshold Scenario Quality Audit

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_lines: 71250
redis_entries: 1250
valid_rows: 1250

## Current default MISB gate constants
- DEFAULT_SHELF_WIDTH_MIN: 0.1
- DEFAULT_SHELF_WIDTH_MAX: 12.0
- DEFAULT_BREAKOUT_VEL_RATIO_MIN: 1.15
- DEFAULT_BREAKOUT_VOL_NORM_MIN: 1.1
- DEFAULT_BREAKOUT_EVENT_RATE_MIN: 1.0
- DEFAULT_BREAKOUT_BUFFER_MIN: 0.2

## Overall raw shelf/kinetic stats
- width_pct_stats: {'n': 1245, 'min': 0.010228958180615507, 'median': 0.046492681668027135, 'mean': 0.05539826925880892, 'p75': 0.06394543323031014, 'p90': 0.08910129196873975, 'p95': 0.1048740871478023, 'max': 0.18221504362279664}
- velocity_ratio_stats: {'n': 1250, 'min': 0.0, 'median': 38.000000000029104, 'mean': 58.56000000000227, 'p75': 98.0000000000291, 'p90': 148.0000000000291, 'p95': 188.0000000000291, 'max': 358.0000000000291}
- volume_norm_stats: {'n': 1250, 'min': 0.0, 'median': 4.583333333333333, 'mean': 4.360058032684802, 'p75': 5.0, 'p90': 5.0, 'p95': 5.0, 'max': 5.0}
- event_rate_norm_stats: {'n': 1250, 'min': 0.0, 'median': 4.583333333333333, 'mean': 4.360058032684802, 'p75': 5.0, 'p90': 5.0, 'p95': 5.0, 'max': 5.0}
- call_extension_stats: {'n': 1250, 'min': 0.0, 'median': 0.0, 'mean': 0.0, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 0.0}
- put_extension_stats: {'n': 1250, 'min': 0.0, 'median': 0.0, 'mean': 0.0, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 0.0}

## Scenario counts
Audit-only. This does not recommend a patch by itself.
### width_min=0.03
- shelf_ok: 984
- shelf_plus_kinetic_ok: 808
- width_stats_when_shelf_ok: {'n': 984, 'min': 0.031139824209290637, 'median': 0.05288026883646971, 'mean': 0.0639403446537536, 'p75': 0.07674269878490728, 'p90': 0.09804966428647553, 'p95': 0.1539902017868773, 'max': 0.18221504362279664}
### width_min=0.05
- shelf_ok: 567
- shelf_plus_kinetic_ok: 471
- width_stats_when_shelf_ok: {'n': 567, 'min': 0.05073966925411175, 'median': 0.0665469390541043, 'mean': 0.08048609644982883, 'p75': 0.08489779201748064, 'p90': 0.12250900142358333, 'p95': 0.18136235130954287, 'max': 0.18221504362279664}
### width_min=0.06
- shelf_ok: 363
- shelf_plus_kinetic_ok: 314
- width_stats_when_shelf_ok: {'n': 363, 'min': 0.060999669407398496, 'median': 0.08358280241195466, 'mean': 0.09465703101220939, 'p75': 0.09804966428647553, 'p90': 0.18136235130954287, 'p95': 0.18136235130954287, 'max': 0.18221504362279664}
### width_min=0.07
- shelf_ok: 264
- shelf_plus_kinetic_ok: 233
- width_stats_when_shelf_ok: {'n': 264, 'min': 0.07120700131113447, 'median': 0.08794849462915853, 'mean': 0.1059518266089842, 'p75': 0.09804966428647553, 'p90': 0.18136235130954287, 'p95': 0.18136235130954287, 'max': 0.18221504362279664}
### width_min=0.075
- shelf_ok: 256
- shelf_plus_kinetic_ok: 225
- width_stats_when_shelf_ok: {'n': 256, 'min': 0.07631651314541901, 'median': 0.08794849462915853, 'mean': 0.106997868729168, 'p75': 0.09804966428647553, 'p90': 0.18136235130954287, 'p95': 0.18136235130954287, 'max': 0.18221504362279664}
### width_min=0.08
- shelf_ok: 217
- shelf_plus_kinetic_ok: 197
- width_stats_when_shelf_ok: {'n': 217, 'min': 0.08015758640390586, 'median': 0.09592571512620626, 'mean': 0.11234459353253246, 'p75': 0.1539902017868773, 'p90': 0.18136235130954287, 'p95': 0.18136235130954287, 'max': 0.18221504362279664}
### width_min=0.09
- shelf_ok: 124
- shelf_plus_kinetic_ok: 116
- width_stats_when_shelf_ok: {'n': 124, 'min': 0.09378863452274375, 'median': 0.1048740871478023, 'mean': 0.13372325719684716, 'p75': 0.18136235130954287, 'p90': 0.18136235130954287, 'p95': 0.18221504362279664, 'max': 0.18221504362279664}
### width_min=0.1
- shelf_ok: 64
- shelf_plus_kinetic_ok: 62
- width_stats_when_shelf_ok: {'n': 64, 'min': 0.1048740871478023, 'median': 0.18136235130954287, 'mean': 0.16800601962009765, 'p75': 0.18136235130954287, 'p90': 0.18221504362279664, 'p95': 0.18221504362279664, 'max': 0.18221504362279664}

## Example rows with width>=0.07 and kinetic_ok
- {'sid': '1780651742435-0', 'ltp': 23463.9, 'width_pct': 0.07631651314541901, 'count': 8.0, 'high': 23463.9, 'low': 23446.0, 'vel': 358.0000000000291, 'vol': 4.285714285714286, 'event': 4.285714285714286, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651743691-0', 'ltp': 23463.9, 'width_pct': 0.07631651314541901, 'count': 9.0, 'high': 23463.9, 'low': 23446.0, 'vel': 358.0000000000291, 'vol': 3.888888888888889, 'event': 3.888888888888889, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651744927-0', 'ltp': 23464.0, 'width_pct': 0.07674269878490728, 'count': 10.0, 'high': 23464.0, 'low': 23446.0, 'vel': 180.0, 'vol': 4.0, 'event': 4.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651745445-0', 'ltp': 23461.8, 'width_pct': 0.07674269878490728, 'count': 11.0, 'high': 23464.0, 'low': 23446.0, 'vel': 42.000000000043656, 'vol': 4.090909090909091, 'event': 4.090909090909091, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651746479-0', 'ltp': 23466.9, 'width_pct': 0.08910129196873975, 'count': 12.0, 'high': 23466.9, 'low': 23446.0, 'vel': 60.0, 'vol': 4.166666666666667, 'event': 4.166666666666667, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651747206-0', 'ltp': 23466.9, 'width_pct': 0.08910129196873975, 'count': 13.0, 'high': 23466.9, 'low': 23446.0, 'vel': 60.0, 'vol': 4.166666666666667, 'event': 4.166666666666667, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651747946-0', 'ltp': 23468.0, 'width_pct': 0.09378863452274375, 'count': 14.0, 'high': 23468.0, 'low': 23446.0, 'vel': 80.0, 'vol': 4.230769230769231, 'event': 4.230769230769231, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651748726-0', 'ltp': 23468.0, 'width_pct': 0.09378863452274375, 'count': 15.0, 'high': 23468.0, 'low': 23446.0, 'vel': 124.00000000001455, 'vol': 4.583333333333333, 'event': 4.583333333333333, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651748959-0', 'ltp': 23463.9, 'width_pct': 0.09378863452274375, 'count': 16.0, 'high': 23468.0, 'low': 23446.0, 'vel': 60.0, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651749432-0', 'ltp': 23469.0, 'width_pct': 0.09804966428647553, 'count': 17.0, 'high': 23469.0, 'low': 23446.0, 'vel': 20.0, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651750453-0', 'ltp': 23461.2, 'width_pct': 0.09804966428647553, 'count': 18.0, 'high': 23469.0, 'low': 23446.0, 'vel': 135.99999999998545, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651750706-0', 'ltp': 23461.2, 'width_pct': 0.09804966428647553, 'count': 19.0, 'high': 23469.0, 'low': 23446.0, 'vel': 135.99999999998545, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651751680-0', 'ltp': 23460.4, 'width_pct': 0.09804966428647553, 'count': 20.0, 'high': 23469.0, 'low': 23446.0, 'vel': 70.0, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651752186-0', 'ltp': 23460.4, 'width_pct': 0.09804966428647553, 'count': 21.0, 'high': 23469.0, 'low': 23446.0, 'vel': 70.0, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651752444-0', 'ltp': 23463.1, 'width_pct': 0.09804966428647553, 'count': 22.0, 'high': 23469.0, 'low': 23446.0, 'vel': 118.0000000000291, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651753681-0', 'ltp': 23466.9, 'width_pct': 0.09804966428647553, 'count': 23.0, 'high': 23469.0, 'low': 23446.0, 'vel': 114.00000000001455, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651755469-0', 'ltp': 23466.9, 'width_pct': 0.09804966428647553, 'count': 24.0, 'high': 23469.0, 'low': 23446.0, 'vel': 130.0, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651755698-0', 'ltp': 23462.1, 'width_pct': 0.09804966428647553, 'count': 25.0, 'high': 23469.0, 'low': 23446.0, 'vel': 20.0, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651756423-0', 'ltp': 23455.0, 'width_pct': 0.09804966428647553, 'count': 26.0, 'high': 23469.0, 'low': 23446.0, 'vel': 238.0000000000291, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}
- {'sid': '1780651757235-0', 'ltp': 23455.0, 'width_pct': 0.09804966428647553, 'count': 27.0, 'high': 23469.0, 'low': 23446.0, 'vel': 238.0000000000291, 'vol': 5.0, 'event': 5.0, 'call_ext': 0.0, 'put_ext': 0.0}

## Interpretation
- A safe MISB expansion should require shelf width plus kinetic and breakout-extension evidence.
- If width_min=0.05 creates too many shelf_ok rows, it may be too loose unless paired with stronger breakout/acceptance gates.
- width_min=0.07 or 0.075 may be the first candidate for further shadow-only study, not production patch.
- No threshold change is made here.

R27C_MISB_THRESHOLD_SCENARIO_QUALITY_AUDIT_OK=True