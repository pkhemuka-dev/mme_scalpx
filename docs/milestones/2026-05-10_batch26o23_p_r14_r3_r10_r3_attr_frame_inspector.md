# 2026-05-10 — 26-O23-P-R14-R3-R10-R3

Verdict: `FAIL_O23_P_R14_R3_R10_R3_ATTRIBUTEERROR_FRAME_NOT_PROVEN`

## AttributeError extraction
- rootcause: `ATTRIBUTEERROR_QUOTE_OBJECT_SHAPE_MISMATCH`
- rootcause_supported: `True`
- attributeerror_extracted: `True`
- source_context_extracted: `True`

## Safety
- source_patch_applied: `False`
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- risk_execution_not_running: `True`

Next: 26-O23-P-R14-R3-R10-R4 patch exact quote object shape conversion only if source_context proves it; compile/import only; no service start, no paper/live.
