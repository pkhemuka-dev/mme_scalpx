# Lane X R15 Observe Restart After OOM + Validate R11

- timestamp: 2026-06-18T10:06:13+05:30
- mode: OBSERVE_ONLY_NO_PAPER_NO_ORDER
- purpose: after R14 Redis OOM relief, restart observe-only services and prove R11 feed refresh works

=== SAFETY BEFORE START ===
=== REDIS MEMORY BEFORE START ===
=== STREAM XLEN BEFORE ===
=== START OBSERVE-ONLY SERVICES ===
started feeds/features/strategy=16847/16851/16857
=== WAIT 60S ===
=== VALIDATE OBSERVE FLOW ===
validate_rc=0
=== SERVICE LOG ERROR GREP ===
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate_stdout.txt:11:    "r11_selected_option_refresh_source_id": "1781757428572-0",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate_stdout.txt:12:    "r11_selected_option_refresh_source_stream": "ticks:mme:opt:stream",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate_stdout.txt:13:    "r11_selected_option_refresh_status": "applied",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate_stdout.txt:14:    "r11_selected_option_refresh_written_at_ns": "1781757428579194123",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate_stdout.txt:21:    "validity_reason": "r11_selected_option_active_market_overlay_from_latest_tick"
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/report.md:15:=== SERVICE LOG ERROR GREP ===
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:11:    "r11_selected_option_refresh_source_id": "1781757428572-0",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:12:    "r11_selected_option_refresh_source_stream": "ticks:mme:opt:stream",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:13:    "r11_selected_option_refresh_status": "applied",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:14:    "r11_selected_option_refresh_written_at_ns": "1781757428579194123",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:21:    "validity_reason": "r11_selected_option_active_market_overlay_from_latest_tick"
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:55:    "r11_selected_option_refresh_source_id": "1781757428572-0",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:56:    "r11_selected_option_refresh_source_stream": "ticks:mme:opt:stream",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:57:    "r11_selected_option_refresh_status": "applied",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:58:    "r11_selected_option_refresh_written_at_ns": "1781757428579194123",
run/audits/LANE-X-LIVE-NOW-R15_OBSERVE_RESTART_AFTER_OOM_VALIDATE_R11_NO_PAPER_NO_ORDER_20260618_100613/r15_validate.json:65:    "validity_reason": "r11_selected_option_active_market_overlay_from_latest_tick"
=== MEMORY AFTER ===
=== FINAL PSTATUS ===
=== FINAL PROCESS SNAPSHOT ===

## R15 verdict
REVIEW_R15_R11_REFRESH_VISIBLE_BUT_FEATURE_SYNC_NOT_OK_NO_PAPER_NO_ORDER
- feature_core: {'market.selected_option_ltp': 125.0, 'provider_runtime.provider_ready_classic': False, 'provider_runtime.provider_ready_miso': False, 'snapshot.fut_opt_skew_ms': 1000, 'snapshot.futures_snapshot_ns': 1781777224000000000, 'snapshot.selected_option_snapshot_ns': 1781777225000000000, 'snapshot.sync_ok': False, 'snapshot.valid': False, 'snapshot.validity': 'MARKETDATA_INCOMPLETE_OR_UNSYNCED', 'stage_flags.provider_ready_classic': False, 'stage_flags.provider_ready_miso': False, 'stage_flags.tradability_ok': False}
- decision_core: {'action': 'HOLD', 'activation_candidate_count': None, 'activation_reason': None, 'candidate_present_shadow': None, 'candidate_true_shadow': None, 'reason': 'candidate_observed_dry_run'}
- active_selected: {'ask': '102.2', 'ask_qty': '455', 'bid': '102.05', 'bid_qty': '65', 'expiry': '2026-06-23', 'instrument_key': 'NFO:NIFTY2662324050PE', 'ltp': '102.0', 'option_side': 'PUT', 'r11_selected_option_refresh_source_id': '1781757428572-0', 'r11_selected_option_refresh_source_stream': 'ticks:mme:opt:stream', 'r11_selected_option_refresh_status': 'applied', 'r11_selected_option_refresh_written_at_ns': '1781757428579194123', 'selected_option_marketdata_status': 'HEALTHY', 'selected_option_snapshot_ns': '1781777227000000000', 'strike': '24050.0', 'trading_symbol': 'NIFTY2662324050PE', 'ts_event_ns': '1781777227000000000', 'validity': 'OK', 'validity_reason': 'r11_selected_option_active_market_overlay_from_latest_tick'}
- services: ['16913 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide', '16914 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap', '16915 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap']
- validate_rc=0
- runtime_started=OBSERVE_ONLY_FEEDS_FEATURES_STRATEGY_ONLY
- paper_armed=NO
- order_attempted=NO
