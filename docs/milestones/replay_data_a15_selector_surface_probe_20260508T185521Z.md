# REPLAY-DATA-A15 — selector-only replay-data surface probe

Generated: 2026-05-08T18:55:21Z

Based on proof: proof_replay_data_a14_execution_shadow_20260508T184835Z.json

Canonical root: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z

Source date: 2026-04-17

Checked surfaces:

- quote_ticks_mme_fut_stream.csv
  - path: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_fut_stream.csv
  - exists: True
  - header: ts_event,symbol,bid,ask,ltp,last,price,bid_qty,ask_qty,volume,oi,provider,instrument_token,source_stream,source_ts_event_ns,source_ts_exchange_ns,source_ts_recv_ns,selection_role,validity,validity_reason
  - row_count: 25017
  - sample_rows:
    - 1776338518000000000,NIFTY26APRFUT,24319.9,24321.0,24317.0,24317.0,24317.0,65.0,390.0,,,ZERODHA,17072898,ticks_mme_fut_stream,1776338518000000000,1776338518000000000,1776318718472666197,FUTURES,ANOMALY_CLAMPED,ltp_anomaly_clamped
    - 1776338518000000000,NIFTY26APRFUT,24316.8,24317.2,24317.0,24317.0,24317.0,260.0,130.0,,,ZERODHA,17072898,ticks_mme_fut_stream,1776338518000000000,1776338518000000000,1776318719231384441,FUTURES,ANOMALY_CLAMPED,ltp_anomaly_clamped
    - 1776338520000000000,NIFTY26APRFUT,24316.8,24317.2,24317.0,24317.0,24317.0,260.0,195.0,,,ZERODHA,17072898,ticks_mme_fut_stream,1776338520000000000,1776338520000000000,1776318720965533804,FUTURES,ANOMALY_CLAMPED,ltp_anomaly_clamped
    - 1776338520000000000,NIFTY26APRFUT,24316.8,24317.2,24317.2,24317.2,24317.2,260.0,195.0,,,ZERODHA,17072898,ticks_mme_fut_stream,1776338520000000000,1776338520000000000,1776318721218590388,FUTURES,ANOMALY_CLAMPED,ltp_anomaly_clamped
    - 1776338522000000000,NIFTY26APRFUT,24316.8,24317.2,24316.8,24316.8,24316.8,130.0,65.0,,,ZERODHA,17072898,ticks_mme_fut_stream,1776338522000000000,1776338522000000000,1776318722443676172,FUTURES,ANOMALY_CLAMPED,ltp_anomaly_clamped

- quote_ticks_mme_opt_stream.csv
  - path: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_opt_stream.csv
  - exists: True
  - header: ts_event,symbol,bid,ask,ltp,last,price,bid_qty,ask_qty,volume,oi,provider,instrument_token,source_stream,source_ts_event_ns,source_ts_exchange_ns,source_ts_recv_ns,selection_role,validity,validity_reason
  - row_count: 25006
  - sample_rows:
    - 1776421122000000000,NIFTY2642124250CE,186.8,187.3,187.5,187.5,187.5,845.0,1365.0,,,ZERODHA,16237570,ticks_mme_opt_stream,1776421122000000000,1776421122000000000,1776401323252936269,CE_ATM1,OK,ok
    - 1776421122000000000,NIFTY2642124200PE,136.4,136.7,136.95,136.95,136.95,1950.0,780.0,,,ZERODHA,16237314,ticks_mme_opt_stream,1776421122000000000,1776421122000000000,1776401323255008561,PE_ATM,OK,ok
    - 1776421122000000000,NIFTY2642124250CE,187.2,187.6,187.25,187.25,187.25,1040.0,260.0,,,ZERODHA,16237570,ticks_mme_opt_stream,1776421122000000000,1776421122000000000,1776401323458467846,CE_ATM1,OK,ok
    - 1776421123000000000,NIFTY2642124150PE,117.85,118.15,118.2,118.2,118.2,975.0,1885.0,,,ZERODHA,16236802,ticks_mme_opt_stream,1776421123000000000,1776421123000000000,1776401323713060671,PE_ATM1,OK,ok
    - 1776421123000000000,NIFTY2642124250CE,187.2,187.6,187.45,187.45,187.45,1040.0,260.0,,,ZERODHA,16237570,ticks_mme_opt_stream,1776421123000000000,1776421123000000000,1776401324220242502,CE_ATM1,OK,ok

- features_rows_candidate.csv
  - path: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/features_rows_candidate.csv
  - exists: True
  - header: ts_event,symbol,side,source_stream,bid,ask,ltp,mid,spread,provider,instrument_token,source_file,source_row_number,source_date
  - row_count: 50022
  - sample_rows:
    - 1776338518000000000,NIFTY26APRFUT,,quote_ticks_mme_fut_stream,24319.9,24321,24317.0,24320.45,1.1,ZERODHA,17072898,run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_fut_stream.csv,1,2026-04-17
    - 1776338518000000000,NIFTY26APRFUT,,quote_ticks_mme_fut_stream,24316.8,24317.2,24317.0,24317,0.4,ZERODHA,17072898,run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_fut_stream.csv,2,2026-04-17
    - 1776338520000000000,NIFTY26APRFUT,,quote_ticks_mme_fut_stream,24316.8,24317.2,24317.0,24317,0.4,ZERODHA,17072898,run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_fut_stream.csv,3,2026-04-17
    - 1776338520000000000,NIFTY26APRFUT,,quote_ticks_mme_fut_stream,24316.8,24317.2,24317.2,24317,0.4,ZERODHA,17072898,run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_fut_stream.csv,4,2026-04-17
    - 1776338522000000000,NIFTY26APRFUT,,quote_ticks_mme_fut_stream,24316.8,24317.2,24316.8,24317,0.4,ZERODHA,17072898,run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/quote_ticks_mme_fut_stream.csv,5,2026-04-17

- strategy_decisions_candidate.csv
  - path: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/strategy_decisions_candidate.csv
  - exists: True
  - header: ts_event,symbol,strategy,decision,action,signal,side,confidence,reason,source_stream,source_provider,instrument_token,source_bid,source_ask,source_ltp,source_mid,source_spread,source_feature_row_index,source_features_sha256
  - row_count: 50022
  - sample_rows:
    - 1776338518000000000,NIFTY26APRFUT,A12_SHADOW_CONSERVATIVE,HOLD,NO_TRADE,HOLD,quote_ticks_mme_fut_stream,0.0,A12 conservative shadow reconstruction from features_rows_candidate; no strategy/risk/execution parity claimed,quote_ticks_mme_fut_stream,ZERODHA,17072898,24319.9,24321,24317.0,24320.45,1.1,1,9dc6b1213353d55857660e0a544065d52270b4b423f7945ab0452710dbbf9510
    - 1776338518000000000,NIFTY26APRFUT,A12_SHADOW_CONSERVATIVE,HOLD,NO_TRADE,HOLD,quote_ticks_mme_fut_stream,0.0,A12 conservative shadow reconstruction from features_rows_candidate; no strategy/risk/execution parity claimed,quote_ticks_mme_fut_stream,ZERODHA,17072898,24316.8,24317.2,24317.0,24317,0.4,2,9dc6b1213353d55857660e0a544065d52270b4b423f7945ab0452710dbbf9510
    - 1776338520000000000,NIFTY26APRFUT,A12_SHADOW_CONSERVATIVE,HOLD,NO_TRADE,HOLD,quote_ticks_mme_fut_stream,0.0,A12 conservative shadow reconstruction from features_rows_candidate; no strategy/risk/execution parity claimed,quote_ticks_mme_fut_stream,ZERODHA,17072898,24316.8,24317.2,24317.0,24317,0.4,3,9dc6b1213353d55857660e0a544065d52270b4b423f7945ab0452710dbbf9510
    - 1776338520000000000,NIFTY26APRFUT,A12_SHADOW_CONSERVATIVE,HOLD,NO_TRADE,HOLD,quote_ticks_mme_fut_stream,0.0,A12 conservative shadow reconstruction from features_rows_candidate; no strategy/risk/execution parity claimed,quote_ticks_mme_fut_stream,ZERODHA,17072898,24316.8,24317.2,24317.2,24317,0.4,4,9dc6b1213353d55857660e0a544065d52270b4b423f7945ab0452710dbbf9510
    - 1776338522000000000,NIFTY26APRFUT,A12_SHADOW_CONSERVATIVE,HOLD,NO_TRADE,HOLD,quote_ticks_mme_fut_stream,0.0,A12 conservative shadow reconstruction from features_rows_candidate; no strategy/risk/execution parity claimed,quote_ticks_mme_fut_stream,ZERODHA,17072898,24316.8,24317.2,24316.8,24317,0.4,5,9dc6b1213353d55857660e0a544065d52270b4b423f7945ab0452710dbbf9510

- risk_outputs_candidate.csv
  - path: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/risk_outputs_candidate.csv
  - exists: True
  - header: ts_event,symbol,side,action,decision,signal,instrument_token,source_stream,risk_allowed,allow,approved,risk_status,risk_decision,risk_reason,order_intent,order_qty,max_qty,risk_rule,source_strategy_row_index,source_strategy_sha256,shadow_reconstruction
  - row_count: 50022
  - sample_rows:
    - 1776338518000000000,NIFTY26APRFUT,quote_ticks_mme_fut_stream,NO_TRADE,HOLD,HOLD,17072898,quote_ticks_mme_fut_stream,false,false,false,risk_blocked,no_order,shadow_conservative_no_order_reconstruction,no_order,0,0,conservative_shadow_default,0,ab070a89d3c2be360930b66fabc2bddaede8fc4e5a06096dc522f99511613d4e,true
    - 1776338518000000000,NIFTY26APRFUT,quote_ticks_mme_fut_stream,NO_TRADE,HOLD,HOLD,17072898,quote_ticks_mme_fut_stream,false,false,false,risk_blocked,no_order,shadow_conservative_no_order_reconstruction,no_order,0,0,conservative_shadow_default,1,ab070a89d3c2be360930b66fabc2bddaede8fc4e5a06096dc522f99511613d4e,true
    - 1776338520000000000,NIFTY26APRFUT,quote_ticks_mme_fut_stream,NO_TRADE,HOLD,HOLD,17072898,quote_ticks_mme_fut_stream,false,false,false,risk_blocked,no_order,shadow_conservative_no_order_reconstruction,no_order,0,0,conservative_shadow_default,2,ab070a89d3c2be360930b66fabc2bddaede8fc4e5a06096dc522f99511613d4e,true
    - 1776338520000000000,NIFTY26APRFUT,quote_ticks_mme_fut_stream,NO_TRADE,HOLD,HOLD,17072898,quote_ticks_mme_fut_stream,false,false,false,risk_blocked,no_order,shadow_conservative_no_order_reconstruction,no_order,0,0,conservative_shadow_default,3,ab070a89d3c2be360930b66fabc2bddaede8fc4e5a06096dc522f99511613d4e,true
    - 1776338522000000000,NIFTY26APRFUT,quote_ticks_mme_fut_stream,NO_TRADE,HOLD,HOLD,17072898,quote_ticks_mme_fut_stream,false,false,false,risk_blocked,no_order,shadow_conservative_no_order_reconstruction,no_order,0,0,conservative_shadow_default,4,ab070a89d3c2be360930b66fabc2bddaede8fc4e5a06096dc522f99511613d4e,true

- execution_shadow_candidate.csv
  - path: run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17/execution_shadow_candidate.csv
  - exists: True
  - header: deterministic_run_id,dataset_hash_present,profile_hash_present,experiment_hash_present,selected_window_hash_present,code_hash_present,event_order_monotonic,reset_cleanliness,artifact_root_is_run_replay,config_root_is_etc_replay,no_broker_call,no_live_redis_write,no_runtime_promotion
  - row_count: 50022
  - sample_rows:
    - ,,,,,,,,,,,,
    - ,,,,,,,,,,,,
    - ,,,,,,,,,,,,
    - ,,,,,,,,,,,,
    - ,,,,,,,,,,,,

Final summary:

- surface_probe_ok: True
- all_required_surfaces_present: True
- engine_ready: False
- next_batch: REPLAY-DATA-A16
