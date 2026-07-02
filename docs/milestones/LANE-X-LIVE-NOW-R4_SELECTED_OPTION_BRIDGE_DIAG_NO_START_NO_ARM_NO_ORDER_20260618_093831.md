# Lane X Live Now R4 Selected Option Bridge Diagnostic

- timestamp: 2026-06-18T09:38:31+05:30
- mode: NO_START_NO_ARM_NO_ORDER
- purpose: compare option tick stream vs selected-option active snapshot/projection

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== PROCESS SNAPSHOT ===
=== SELECTED OPTION BRIDGE DIAG ===
diag_rc=0
=== PSTATUS AFTER ===
=== FINAL PROCESS SNAPSHOT ===

## R4 verdict
REVIEW_R4_OPTION_TICK_HAS_DATA_BUT_SELECTED_ACTIVE_SNAPSHOT_MISSING_FIELDS_NO_START_NO_ARM_NO_ORDER
- missing_in_selected_active_from_latest_opt_tick: ['ltp', 'trading_symbol', 'instrument_key', 'instrument_token', 'bid', 'ask', 'bid_qty', 'ask_qty', 'option_side', 'strike', 'expiry', 'ts_event_ns']
- diag_rc=0
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
