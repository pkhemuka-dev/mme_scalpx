# Lane X R12 Observe-only Reload + Validate R11

- timestamp: 2026-06-18T09:58:29+05:30
- mode: OBSERVE_ONLY_RELOAD_NO_PAPER_NO_ORDER
- purpose: reload patched feeds.py and prove R11 selected-option refresh runs naturally

## Safety env
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_DHAN_ACCESS_TOKEN=***MASKED***
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== BEFORE PSTATUS ===
=== BEFORE PROCESS SNAPSHOT ===
=== SAFETY GATES BEFORE RELOAD ===
position has_position=0 qty_lots=0 qty_units=0
streams orders/risk/execution=0/0/0
processes risk/execution=0/0
=== STREAM XLEN BEFORE RELOAD ===
=== STOP OLD OBSERVE-ONLY FEEDS/FEATURES/STRATEGY ONLY ===
stop_rc=0
=== START OBSERVE-ONLY FEEDS / FEATURES / STRATEGY WITH PATCHED CODE ===
started feeds/features/strategy=16079/16083/16087
=== WAIT 75S FOR OBSERVE FLOW ===
=== VALIDATE R11 NATURAL REFRESH + FEATURE/DECISION FLOW ===
validate_rc=0
=== AFTER PSTATUS ===
=== AFTER PROCESS SNAPSHOT ===

## R12 verdict
REVIEW_R12_R11_REFRESH_NOT_VISIBLE_AFTER_RELOAD_NO_PAPER_NO_ORDER
- feature_core: {'market.selected_option_ltp': 120.55, 'provider_runtime.provider_ready_classic': False, 'provider_runtime.provider_ready_miso': False, 'snapshot.fut_opt_skew_ms': 177000, 'snapshot.futures_snapshot_ns': 1781776271000000000, 'snapshot.selected_option_snapshot_ns': 1781776094000000000, 'snapshot.sync_ok': False, 'snapshot.valid': False, 'snapshot.validity': 'MARKETDATA_INCOMPLETE_OR_UNSYNCED', 'stage_flags.provider_ready_classic': False, 'stage_flags.provider_ready_miso': False, 'stage_flags.tradability_ok': False}
- decision_core: {'action': 'HOLD', 'activation_candidate_count': None, 'activation_reason': None, 'candidate_present_shadow': None, 'candidate_true_shadow': None, 'reason': 'no_candidate'}
- active_selected: {'ask': '119.5', 'ask_qty': '130', 'bid': '119.4', 'bid_qty': '195', 'expiry': '2026-06-23', 'instrument_key': 'NFO:NIFTY2662324100PE', 'ltp': '119.6', 'option_side': 'PUT', 'r11_selected_option_refresh_source_id': None, 'r11_selected_option_refresh_source_stream': None, 'r11_selected_option_refresh_status': None, 'r11_selected_option_refresh_written_at_ns': None, 'selected_option_marketdata_status': 'HEALTHY', 'selected_option_snapshot_ns': '1781776094000000000', 'strike': '24100.0', 'trading_symbol': 'NIFTY2662324100PE', 'ts_event_ns': '1781776094000000000', 'validity': 'OK', 'validity_reason': 'ok'}
- stop_rc=0
- validate_rc=0
- runtime_started=OBSERVE_ONLY_FEEDS_FEATURES_STRATEGY_ONLY
- paper_armed=NO
- order_attempted=NO
- redis_delete_attempted=NO
