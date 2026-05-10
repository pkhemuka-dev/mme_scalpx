# 2026-05-10 — 26-O23-P-R14-R3-R11-R6

Verdict: `FAIL_O23_P_R14_R3_R11_R6_SELECTED_LTP_SEVERE_LOG_NOT_PROVEN`

## Classification
- rootcause: `SELECTED_LTP_STILL_REJECTED_BY_INSTRUMENT_VALIDATION`
- rootcause_supported: `True`
- selected_ltp: `22350.0`
- exceptions: `["TypeError: unsupported operand type(s) for /: 'float' and 'decimal.Decimal'"]`
- traceback_extracted: `True`
- exception_line_extracted: `True`
- source_context_extracted: `True`

## Safety
- source_patch_applied: `False`
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- risk_execution_not_running: `True`

Next: 26-O23-P-R14-R3-R11-R7 inspect selected fallback propagation into runtime instruments; patch only exact source-proven conversion path; no service start, no paper/live.
