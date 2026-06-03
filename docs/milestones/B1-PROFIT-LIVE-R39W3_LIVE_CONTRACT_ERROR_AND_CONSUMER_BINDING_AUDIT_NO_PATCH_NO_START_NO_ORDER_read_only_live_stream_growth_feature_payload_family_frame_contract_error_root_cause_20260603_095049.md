# B1-PROFIT-LIVE-R39W3_LIVE_CONTRACT_ERROR_AND_CONSUMER_BINDING_AUDIT_NO_PATCH_NO_START_NO_ORDER_read_only_live_stream_growth_feature_payload_family_frame_contract_error_root_cause_20260603_095049

Classification: `BLOCKED_R39W3_SELECTED_IDENTITY_PRESENT_BUT_PAYLOAD_FRAME_UNSYNCED_NO_PATCH`

## Growth
- decisions: before=2131 after=2297 growth=166
- errors: before=10015 after=10015 growth=0
- execution: before=0 after=0 growth=0
- features: before=4318 after=4354 growth=36
- fut_zerodha: before=149 after=221 growth=72
- opt_selected_zerodha: before=714 after=961 growth=247
- orders: before=0 after=0 growth=0
- provider_runtime: before=1250 after=1721 growth=471
- risk: before=0 after=0 growth=0

## Provider runtime
- selected_option_marketdata_provider_id: ZERODHA
- selected_option_marketdata_status: FAILOVER_ACTIVE
- futures_marketdata_provider_id: ZERODHA
- futures_marketdata_status: HEALTHY
- option_context_provider_id: DHAN
- option_context_status: UNAVAILABLE
- family_runtime_mode: OBSERVE_ONLY
- failover_active: True
- pending_failover: False

## Feature state
- frame_valid: True
- selected_option: `{"delta_3": null, "depth_ok": true, "depth_total": 1950.0, "ltp": 143.3, "micro_edge": null, "microprice": null, "ofi_ratio_proxy": null, "response_efficiency": 0.0, "side": "CALL", "spread": 0.35000000000002274, "spread_ratio": 0.0024313997915944617, "tradability_ok": true}`

## Payload snapshot
- valid: True
- validity: OK
- sync_ok: False
- freshness_ok: True
- packet_gap_ok: True
- warmup_ok: True
- active_snapshot_ns: 1780480367000000000
- futures_snapshot_ns: 1780480367000000000
- selected_option_snapshot_ns: None
- dhan_futures_snapshot_ns: None
- dhan_option_snapshot_ns: None
- max_member_age_ms: 0
- fut_opt_skew_ms: None
- hard_packet_gap_ms: 1000
- samples_seen: 1

## Family identity summary
- mist_call: {'instrument_key': '10825218', 'instrument_token': '10825218', 'option_symbol': 'NIFTY2660923250CE', 'strike': 23250.0, 'option_price': 240.05, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- mist_put: {'instrument_key': '10825474', 'instrument_token': '10825474', 'option_symbol': 'NIFTY2660923250PE', 'strike': 23250.0, 'option_price': 165.25, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- misb_call: {'instrument_key': '10825218', 'instrument_token': '10825218', 'option_symbol': 'NIFTY2660923250CE', 'strike': 23250.0, 'option_price': 240.05, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- misb_put: {'instrument_key': '10825474', 'instrument_token': '10825474', 'option_symbol': 'NIFTY2660923250PE', 'strike': 23250.0, 'option_price': 165.25, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- misc_call: {'instrument_key': '10825218', 'instrument_token': '10825218', 'option_symbol': 'NIFTY2660923250CE', 'strike': 23250.0, 'option_price': 240.05, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- misc_put: {'instrument_key': '10825474', 'instrument_token': '10825474', 'option_symbol': 'NIFTY2660923250PE', 'strike': 23250.0, 'option_price': 165.25, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- misr_call: {'instrument_key': '10825218', 'instrument_token': '10825218', 'option_symbol': 'NIFTY2660923250CE', 'strike': 23250.0, 'option_price': 240.05, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- misr_put: {'instrument_key': '10825474', 'instrument_token': '10825474', 'option_symbol': 'NIFTY2660923250PE', 'strike': 23250.0, 'option_price': 165.25, 'eligible': False, 'tradability_ok': False, 'runtime_mode': 'NORMAL', 'active_selected_option_provider_id': 'ZERODHA'}
- miso_call: {'instrument_key': '10825218', 'instrument_token': '10825218', 'option_symbol': 'NIFTY2660923250CE', 'strike': 23250.0, 'option_price': 240.05, 'eligible': False, 'tradability_ok': True, 'runtime_mode': 'DISABLED', 'active_selected_option_provider_id': 'ZERODHA'}
- miso_put: {'instrument_key': '10825474', 'instrument_token': '10825474', 'option_symbol': 'NIFTY2660923250PE', 'strike': 23250.0, 'option_price': 165.25, 'eligible': False, 'tradability_ok': True, 'runtime_mode': 'DISABLED', 'active_selected_option_provider_id': 'ZERODHA'}

## FeatureFamilyContractError
- count_in_tail: 8
- id=1780460135658-0 fields={"error": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')", "error_type": "FeatureFamilyContractError", "instance_id": "strategy:mme-scalpx:1864", "service": "strategy", "ts_event_ns": "1780460135657727157", "ts_ns": "1780460135657727157", "where": "strategy_hold_bridge_loop_error"}
- id=1780460135273-0 fields={"error": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')", "error_type": "FeatureFamilyContractError", "instance_id": "strategy:mme-scalpx:1864", "service": "strategy", "ts_event_ns": "1780460135273362738", "ts_ns": "1780460135273362738", "where": "strategy_hold_bridge_loop_error"}
- id=1780460134884-0 fields={"error": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')", "error_type": "FeatureFamilyContractError", "instance_id": "strategy:mme-scalpx:1864", "service": "strategy", "ts_event_ns": "1780460134883808337", "ts_ns": "1780460134883808337", "where": "strategy_hold_bridge_loop_error"}
- id=1780460134528-0 fields={"error": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')", "error_type": "FeatureFamilyContractError", "instance_id": "strategy:mme-scalpx:1864", "service": "strategy", "ts_event_ns": "1780460134527722133", "ts_ns": "1780460134527722133", "where": "strategy_hold_bridge_loop_error"}
- id=1780460134141-0 fields={"error": "common keys mismatch. expected=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals') actual=('regime', 'strategy_runtime_mode_classic', 'strategy_runtime_mode_miso', 'futures', 'call', 'put', 'selected_option', 'cross_option', 'economics', 'signals', 'family_runtime_mode', 'active_futures_provider_id', 'active_selected_option_provider_id', 'active_option_context_provider_id')", "error_type": "FeatureFamilyContractError", "instance_id": "strategy:mme-scalpx:1864", "service": "strategy", "ts_event_ns": "1780460134140519175", "ts_ns": "1780460134140519175", "where": "strategy_hold_bridge_loop_error"}

## Raw files
- raw_dir: `run/audits/B1-PROFIT-LIVE-R39W3_LIVE_CONTRACT_ERROR_AND_CONSUMER_BINDING_AUDIT_NO_PATCH_NO_START_NO_ORDER_read_only_live_stream_growth_feature_payload_family_frame_contract_error_root_cause_20260603_095049_raw`

## Next route
- If FeatureFamilyContractError is growing, inspect exact contract field mismatch before any patch.
- If selected identity is present but payload snapshot remains unsynced, audit snapshot validity/source mapping.
- If decisions grow and blockers are explicit, continue observe-only capture.
- Paper remains blocked.