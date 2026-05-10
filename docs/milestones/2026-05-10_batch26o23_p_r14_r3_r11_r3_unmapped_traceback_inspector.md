# 2026-05-10 — 26-O23-P-R14-R3-R11-R3

Verdict: `FAIL_O23_P_R14_R3_R11_R3_UNMAPPED_TRACEBACK_NOT_PROVEN`

## Traceback extraction
- rootcause: `POST_QUOTE_SHAPE_TRACEBACK_STILL_UNMAPPED_AFTER_DEEP_EXTRACT`
- rootcause_supported: `False`
- exceptions: `['app.mme_scalpx.domain.instruments.InstrumentValidationError: invalid underlying_ltp: 0.0']`
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

Next: Inspect R11-R3 manual trace extract before any patch; no service start, no paper/live.
