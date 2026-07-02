# R27D MISB Current-Inclusive Shelf Reference Audit

fut_path: run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260605_152027/fut_zerodha.redisraw.gz
raw_lines: 71250
valid_ltp_rows: 1250

## Source risk clue
- source_current_inclusive_risk: True
- Meaning: if current LTP is appended before shelf high/low calculation, breakout extension against that shelf is often zero.

## Current-inclusive shelf extension stats
- call_extension_stats: {'n': 1248, 'min': 0.0, 'median': 0.0, 'mean': 0.0, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 0.0}
- put_extension_stats: {'n': 1248, 'min': 0.0, 'median': 0.0, 'mean': 0.0, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 0.0}
- current_call_breakouts_ge_0_20: 0
- current_put_breakouts_ge_0_20: 0
- width_pct_stats: {'n': 1248, 'min': 0.0, 'median': 0.046492681668027135, 'mean': 0.0552651003423214, 'p75': 0.06394543323031014, 'p90': 0.08910129196873975, 'p95': 0.1048740871478023, 'max': 0.18221504362279664}

## Prior-only shelf extension stats
- call_extension_stats: {'n': 1247, 'min': 0.0, 'median': 0.0, 'mean': 0.0758620689655219, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 9.0}
- put_extension_stats: {'n': 1247, 'min': 0.0, 'median': 0.0, 'mean': 0.05292702485966319, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 6.0}
- prior_call_breakouts_ge_0_20: 43
- prior_put_breakouts_ge_0_20: 32
- width_pct_stats: {'n': 1247, 'min': 0.0, 'median': 0.045629678907790634, 'mean': 0.054760143795478895, 'p75': 0.06394543323031014, 'p90': 0.08794849462915853, 'p95': 0.09804966428647553, 'max': 0.18221504362279664}

## Examples where prior-only sees breakout but current-inclusive erases extension
- {'sid': '1780651741718-0', 'ltp': 23455.0, 'prior_high': 23446.0, 'prior_low': 23446.0, 'prior_call_ext': 9.0, 'prior_put_ext': 0.0, 'current_inclusive_high': 23455.0, 'current_inclusive_low': 23446.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.0, 'current_inclusive_width_pct': 0.03837871260740709}
- {'sid': '1780651742435-0', 'ltp': 23463.9, 'prior_high': 23455.0, 'prior_low': 23446.0, 'prior_call_ext': 8.900000000001455, 'prior_put_ext': 0.0, 'current_inclusive_high': 23463.9, 'current_inclusive_low': 23446.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.03837871260740709, 'current_inclusive_width_pct': 0.07631651314541901}
- {'sid': '1780651746479-0', 'ltp': 23466.9, 'prior_high': 23464.0, 'prior_low': 23446.0, 'prior_call_ext': 2.900000000001455, 'prior_put_ext': 0.0, 'current_inclusive_high': 23466.9, 'current_inclusive_low': 23446.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.07674269878490728, 'current_inclusive_width_pct': 0.08910129196873975}
- {'sid': '1780651747946-0', 'ltp': 23468.0, 'prior_high': 23466.9, 'prior_low': 23446.0, 'prior_call_ext': 1.0999999999985448, 'prior_put_ext': 0.0, 'current_inclusive_high': 23468.0, 'current_inclusive_low': 23446.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.08910129196873975, 'current_inclusive_width_pct': 0.09378863452274375}
- {'sid': '1780651749432-0', 'ltp': 23469.0, 'prior_high': 23468.0, 'prior_low': 23446.0, 'prior_call_ext': 1.0, 'prior_put_ext': 0.0, 'current_inclusive_high': 23469.0, 'current_inclusive_low': 23446.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.09378863452274375, 'current_inclusive_width_pct': 0.09804966428647553}
- {'sid': '1780651938442-0', 'ltp': 23425.5, 'prior_high': 23425.0, 'prior_low': 23420.0, 'prior_call_ext': 0.5, 'prior_put_ext': 0.0, 'current_inclusive_high': 23425.5, 'current_inclusive_low': 23420.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.021346995410395985, 'current_inclusive_width_pct': 0.023481444322293495}
- {'sid': '1780651942477-0', 'ltp': 23429.0, 'prior_high': 23425.5, 'prior_low': 23420.0, 'prior_call_ext': 3.5, 'prior_put_ext': 0.0, 'current_inclusive_high': 23429.0, 'current_inclusive_low': 23420.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.023481444322293495, 'current_inclusive_width_pct': 0.03842131102051271}
- {'sid': '1780651942688-0', 'ltp': 23429.8, 'prior_high': 23429.0, 'prior_low': 23420.0, 'prior_call_ext': 0.7999999999992724, 'prior_put_ext': 0.0, 'current_inclusive_high': 23429.8, 'current_inclusive_low': 23420.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.03842131102051271, 'current_inclusive_width_pct': 0.0418358242724591}
- {'sid': '1780651947521-0', 'ltp': 23430.0, 'prior_high': 23429.8, 'prior_low': 23420.0, 'prior_call_ext': 0.2000000000007276, 'prior_put_ext': 0.0, 'current_inclusive_high': 23430.0, 'current_inclusive_low': 23420.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.0418358242724591, 'current_inclusive_width_pct': 0.042689434364994665}
- {'sid': '1780651951468-0', 'ltp': 23432.0, 'prior_high': 23430.0, 'prior_low': 23420.0, 'prior_call_ext': 2.0, 'prior_put_ext': 0.0, 'current_inclusive_high': 23432.0, 'current_inclusive_low': 23420.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.042689434364994665, 'current_inclusive_width_pct': 0.05122513446597797}
- {'sid': '1780651957484-0', 'ltp': 23435.0, 'prior_high': 23432.0, 'prior_low': 23420.0, 'prior_call_ext': 3.0, 'prior_put_ext': 0.0, 'current_inclusive_high': 23435.0, 'current_inclusive_low': 23420.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.05122513446597797, 'current_inclusive_width_pct': 0.06402731832248426}
- {'sid': '1780651976681-0', 'ltp': 23435.5, 'prior_high': 23435.0, 'prior_low': 23421.0, 'prior_call_ext': 0.5, 'prior_put_ext': 0.0, 'current_inclusive_high': 23435.5, 'current_inclusive_low': 23421.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.0597575550623186, 'current_inclusive_width_pct': 0.061891093018044456}
- {'sid': '1780651978690-0', 'ltp': 23436.0, 'prior_high': 23435.6, 'prior_low': 23423.3, 'prior_call_ext': 0.4000000000014552, 'prior_put_ext': 0.0, 'current_inclusive_high': 23436.0, 'current_inclusive_low': 23423.3, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.052498031323822254, 'current_inclusive_width_pct': 0.05420482166827387}
- {'sid': '1780651980729-0', 'ltp': 23439.8, 'prior_high': 23436.0, 'prior_low': 23425.0, 'prior_call_ext': 3.7999999999992724, 'prior_put_ext': 0.0, 'current_inclusive_high': 23439.8, 'current_inclusive_low': 23425.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.04694735494334308, 'current_inclusive_width_pct': 0.06316041037196049}
- {'sid': '1780651981724-0', 'ltp': 23441.0, 'prior_high': 23439.8, 'prior_low': 23425.0, 'prior_call_ext': 1.2000000000007276, 'prior_put_ext': 0.0, 'current_inclusive_high': 23441.0, 'current_inclusive_low': 23425.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.06316041037196049, 'current_inclusive_width_pct': 0.06827977638373234}
- {'sid': '1780651987235-0', 'ltp': 23448.0, 'prior_high': 23441.0, 'prior_low': 23425.6, 'prior_call_ext': 7.0, 'prior_put_ext': 0.0, 'current_inclusive_high': 23448.0, 'current_inclusive_low': 23425.6, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.06571844341173226, 'current_inclusive_width_pct': 0.09557618787548408}
- {'sid': '1780651997470-0', 'ltp': 23449.9, 'prior_high': 23448.0, 'prior_low': 23430.0, 'prior_call_ext': 1.9000000000014552, 'prior_put_ext': 0.0, 'current_inclusive_high': 23449.9, 'current_inclusive_low': 23430.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.07679508511455267, 'current_inclusive_width_pct': 0.08489779201748064}
- {'sid': '1780652067746-0', 'ltp': 23451.9, 'prior_high': 23450.0, 'prior_low': 23440.0, 'prior_call_ext': 1.9000000000014552, 'prior_put_ext': 0.0, 'current_inclusive_high': 23451.9, 'current_inclusive_low': 23440.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.04265301770100234, 'current_inclusive_width_pct': 0.05075503445158527}
- {'sid': '1780652077495-0', 'ltp': 23457.0, 'prior_high': 23452.0, 'prior_low': 23440.0, 'prior_call_ext': 5.0, 'prior_put_ext': 0.0, 'current_inclusive_high': 23457.0, 'current_inclusive_low': 23440.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.05118143819841338, 'current_inclusive_width_pct': 0.07249930699191846}
- {'sid': '1780652078438-0', 'ltp': 23459.6, 'prior_high': 23457.0, 'prior_low': 23440.0, 'prior_call_ext': 2.599999999998545, 'prior_put_ext': 0.0, 'current_inclusive_high': 23459.6, 'current_inclusive_low': 23440.0, 'current_inclusive_call_ext': 0.0, 'current_inclusive_put_ext': 0.0, 'prior_width_pct': 0.07249930699191846, 'current_inclusive_width_pct': 0.08358280241195466}

## Interpretation
- If prior-only breakout counts are much higher than current-inclusive counts, MISB is not just a width-threshold problem.
- It means micro_shelf is suitable for range measurement but not as a breakout reference when it includes the current breakout tick.
- Correct future patch direction would be additive: publish prior_shelf_high/prior_shelf_low or breakout_ref_high/low from history before appending current tick.
- No patch is applied here.

R27D_MISB_CURRENT_INCLUSIVE_SHELF_REFERENCE_AUDIT_OK=True