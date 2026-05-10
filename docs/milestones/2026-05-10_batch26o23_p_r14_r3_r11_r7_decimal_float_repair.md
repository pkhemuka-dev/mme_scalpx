# 2026-05-10 — 26-O23-P-R14-R3-R11-R7

Verdict: `FAIL_O23_P_R14_R3_R11_R7_DECIMAL_FLOAT_REPAIR_NOT_PROVEN`

## Repair
- float_decimal_exception: `True`
- source_proven_conversion_path: `True`
- patch_applied: `True`
- patch_reason: `patched_runtime_instruments_underlying_ltp_decimal_conversion:{'pattern': '(?P<indent>^[ \\t]*underlying_ltp\\s*=\\s*)(?P<expr>[A-Za-z0-9_\\.]+\\.ltp)(?P<tail>[^\\n]*$)', 'expr': 'quote.ltp'}`
- patched_file: `app/mme_scalpx/integrations/runtime_instruments_factory.py`
- compile_ok: `True`
- import_ok: `True`

## Safety
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- risk_execution_not_running: `True`

Next: 26-O23-P-R14-R3-R11-R8 off-market selected-LTP read-only service liveness rerun after Decimal/float repair; no paper/live.
