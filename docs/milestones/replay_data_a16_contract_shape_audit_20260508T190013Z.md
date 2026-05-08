# REPLAY-DATA-A16 — contract/shape compatibility audit

- timestamp_utc: 20260508T190013Z
- canonical_root: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z
- source_date: 2026-04-17
- date_dir: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17
- contract_shape_ok: True
- engine_ready_candidate: False
- next_batch: REPLAY-DATA-A17

## Accepted file stems discovered in replay code (heuristic)
- 01_trade_log.csv
- 02_candidate_log.csv
- 03_blocker_chain.csv
- 04_side_split_summary.csv
- 05_family_split_summary.csv
- 05_trade_log.csv
- 06_candidate_audit.csv
- 06_scenario_summary.csv
- 07_pnl_execution_shadow_summary.csv
- 11_run_summary.csv
- 12_parameter_surface.csv
- 13_feature_gate_surface.csv
- 14_trade_log_detailed.csv
- 15_candidate_audit_detailed.csv
- 21_comparison_summary.csv
- 22_trade_diff.csv
- 23_blocker_diff.csv
- 24_regime_diff.csv
- 25_feature_gate_diff.csv
- comparison_registry.csv
- feature_gate_registry.csv
- parameter_registry.csv
- run_registry.csv

## Missing expected surfaces
- none

## Incompatible surfaces (header mismatch)
- none detected (or expected header not available for comparison)

## Per-file quick report
- quote_ticks_mme_fut_stream.csv: exists=True, row_count=25016, header='ts_event,symbol,bid,ask,ltp,last,price,bid_qty,ask_qty,volume,oi,provider,instrument_token,source_stream,source_ts_event_ns,source_ts_exchange_ns,source_ts_recv_ns,selection_role,validity,validity_reason'
- quote_ticks_mme_opt_stream.csv: exists=True, row_count=25005, header='ts_event,symbol,bid,ask,ltp,last,price,bid_qty,ask_qty,volume,oi,provider,instrument_token,source_stream,source_ts_event_ns,source_ts_exchange_ns,source_ts_recv_ns,selection_role,validity,validity_reason'
- features_rows_candidate.csv: exists=True, row_count=50021, header='ts_event,symbol,side,source_stream,bid,ask,ltp,mid,spread,provider,instrument_token,source_file,source_row_number,source_date'
- strategy_decisions_candidate.csv: exists=True, row_count=50021, header='ts_event,symbol,strategy,decision,action,signal,side,confidence,reason,source_stream,source_provider,instrument_token,source_bid,source_ask,source_ltp,source_mid,source_spread,source_feature_row_index,source_features_sha256'
- risk_outputs_candidate.csv: exists=True, row_count=50021, header='ts_event,symbol,side,action,decision,signal,instrument_token,source_stream,risk_allowed,allow,approved,risk_status,risk_decision,risk_reason,order_intent,order_qty,max_qty,risk_rule,source_strategy_row_index,source_strategy_sha256,shadow_reconstruction'
- execution_shadow_candidate.csv: exists=True, row_count=50021, header='deterministic_run_id,dataset_hash_present,profile_hash_present,experiment_hash_present,selected_window_hash_present,code_hash_present,event_order_monotonic,reset_cleanliness,artifact_root_is_run_replay,config_root_is_etc_replay,no_broker_call,no_live_redis_write,no_runtime_promotion'

## Notes
- This audit did not run the replay engine nor start any services.
- SCALPX_OBSERVE_ONLY was set for the runtime of this package.
- If contract_shape_ok == True then candidate surfaces match expectations; proceed with caution to the next batch.