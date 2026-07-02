# LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_095409
2026-06-08T09:54:09+05:30

LAW=TEN_MIN_CANDIDATE_WATCH_ONLY_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31D5S proof
R31D5S=run/proofs/LANE-X-R31D5S_EXISTING_GENERIC_MAIN_OBSERVE_ONLY_RUNTIME_SAFETY_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_095109.json
{
  "tag": "LANE-X-R31D5S_EXISTING_GENERIC_MAIN_OBSERVE_ONLY_RUNTIME_SAFETY_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_095109",
  "classification": "PASS_R31D5S_EXISTING_GENERIC_MAIN_OBSERVE_ONLY_SAFE_FOR_R31E_CANDIDATE_WATCH",
  "patch_applied": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "next_lane_x_batch_if_pass": "LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION",
  "report": "run/audits/LANE-X-R31D5S_EXISTING_GENERIC_MAIN_OBSERVE_ONLY_RUNTIME_SAFETY_AUDIT_NO_PATCH_NO_START_NO_ORDER_20260608_095109_report.md"
}

## Safety before window
37464 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0
fut_zerodha_before=251
opt_selected_zerodha_before=1280
features_before=15
decisions_before=2405

## 10-minute observe-only candidate watch begins
WATCH_TICK i=1 now=2026-06-08T09:54:10+05:30 fut=251 opt=1280 features=15 decisions=2405 orders=0 risk=0 execution=0
WATCH_TICK i=2 now=2026-06-08T09:54:20+05:30 fut=253 opt=1300 features=17 decisions=2416 orders=0 risk=0 execution=0
WATCH_TICK i=3 now=2026-06-08T09:54:30+05:30 fut=257 opt=1318 features=19 decisions=2426 orders=0 risk=0 execution=0
WATCH_TICK i=4 now=2026-06-08T09:54:40+05:30 fut=260 opt=1336 features=21 decisions=2436 orders=0 risk=0 execution=0
WATCH_TICK i=5 now=2026-06-08T09:54:50+05:30 fut=266 opt=1354 features=24 decisions=2448 orders=0 risk=0 execution=0
WATCH_TICK i=6 now=2026-06-08T09:55:00+05:30 fut=270 opt=1373 features=26 decisions=2457 orders=0 risk=0 execution=0
WATCH_TICK i=7 now=2026-06-08T09:55:10+05:30 fut=275 opt=1390 features=28 decisions=2467 orders=0 risk=0 execution=0
WATCH_TICK i=8 now=2026-06-08T09:55:20+05:30 fut=280 opt=1407 features=30 decisions=2478 orders=0 risk=0 execution=0
WATCH_TICK i=9 now=2026-06-08T09:55:30+05:30 fut=284 opt=1425 features=32 decisions=2489 orders=0 risk=0 execution=0
WATCH_TICK i=10 now=2026-06-08T09:55:40+05:30 fut=289 opt=1440 features=34 decisions=2499 orders=0 risk=0 execution=0
WATCH_TICK i=11 now=2026-06-08T09:55:50+05:30 fut=293 opt=1459 features=36 decisions=2509 orders=0 risk=0 execution=0
WATCH_TICK i=12 now=2026-06-08T09:56:00+05:30 fut=296 opt=1479 features=39 decisions=2519 orders=0 risk=0 execution=0
WATCH_TICK i=13 now=2026-06-08T09:56:10+05:30 fut=299 opt=1498 features=41 decisions=2530 orders=0 risk=0 execution=0
WATCH_TICK i=14 now=2026-06-08T09:56:21+05:30 fut=302 opt=1516 features=43 decisions=2541 orders=0 risk=0 execution=0
WATCH_TICK i=15 now=2026-06-08T09:56:31+05:30 fut=308 opt=1534 features=45 decisions=2551 orders=0 risk=0 execution=0
WATCH_TICK i=16 now=2026-06-08T09:56:41+05:30 fut=313 opt=1552 features=47 decisions=2561 orders=0 risk=0 execution=0
WATCH_TICK i=17 now=2026-06-08T09:56:51+05:30 fut=315 opt=1572 features=49 decisions=2572 orders=0 risk=0 execution=0
WATCH_TICK i=18 now=2026-06-08T09:57:01+05:30 fut=317 opt=1594 features=51 decisions=2583 orders=0 risk=0 execution=0
WATCH_TICK i=19 now=2026-06-08T09:57:11+05:30 fut=321 opt=1613 features=53 decisions=2594 orders=0 risk=0 execution=0
WATCH_TICK i=20 now=2026-06-08T09:57:21+05:30 fut=323 opt=1634 features=56 decisions=2603 orders=0 risk=0 execution=0
WATCH_TICK i=21 now=2026-06-08T09:57:31+05:30 fut=327 opt=1651 features=58 decisions=2613 orders=0 risk=0 execution=0
WATCH_TICK i=22 now=2026-06-08T09:57:41+05:30 fut=331 opt=1669 features=60 decisions=2623 orders=0 risk=0 execution=0
WATCH_TICK i=23 now=2026-06-08T09:57:51+05:30 fut=333 opt=1685 features=62 decisions=2632 orders=0 risk=0 execution=0
WATCH_TICK i=24 now=2026-06-08T09:58:01+05:30 fut=337 opt=1705 features=64 decisions=2642 orders=0 risk=0 execution=0
WATCH_TICK i=25 now=2026-06-08T09:58:11+05:30 fut=339 opt=1725 features=66 decisions=2653 orders=0 risk=0 execution=0
WATCH_TICK i=26 now=2026-06-08T09:58:21+05:30 fut=345 opt=1740 features=68 decisions=2663 orders=0 risk=0 execution=0
WATCH_TICK i=27 now=2026-06-08T09:58:32+05:30 fut=350 opt=1758 features=70 decisions=2673 orders=0 risk=0 execution=0
WATCH_TICK i=28 now=2026-06-08T09:58:42+05:30 fut=353 opt=1779 features=72 decisions=2684 orders=0 risk=0 execution=0
WATCH_TICK i=29 now=2026-06-08T09:58:52+05:30 fut=357 opt=1797 features=74 decisions=2695 orders=0 risk=0 execution=0
WATCH_TICK i=30 now=2026-06-08T09:59:02+05:30 fut=362 opt=1809 features=76 decisions=2704 orders=0 risk=0 execution=0
WATCH_TICK i=31 now=2026-06-08T09:59:12+05:30 fut=367 opt=1824 features=78 decisions=2714 orders=0 risk=0 execution=0
WATCH_TICK i=32 now=2026-06-08T09:59:22+05:30 fut=371 opt=1841 features=80 decisions=2723 orders=0 risk=0 execution=0
WATCH_TICK i=33 now=2026-06-08T09:59:32+05:30 fut=376 opt=1862 features=82 decisions=2733 orders=0 risk=0 execution=0
WATCH_TICK i=34 now=2026-06-08T09:59:42+05:30 fut=379 opt=1882 features=84 decisions=2743 orders=0 risk=0 execution=0
WATCH_TICK i=35 now=2026-06-08T09:59:52+05:30 fut=383 opt=1902 features=87 decisions=2752 orders=0 risk=0 execution=0
WATCH_TICK i=36 now=2026-06-08T10:00:02+05:30 fut=386 opt=1918 features=89 decisions=2763 orders=0 risk=0 execution=0
WATCH_TICK i=37 now=2026-06-08T10:00:12+05:30 fut=391 opt=1937 features=91 decisions=2773 orders=0 risk=0 execution=0
WATCH_TICK i=38 now=2026-06-08T10:00:22+05:30 fut=396 opt=1950 features=92 decisions=2782 orders=0 risk=0 execution=0
WATCH_TICK i=39 now=2026-06-08T10:00:33+05:30 fut=399 opt=1969 features=94 decisions=2792 orders=0 risk=0 execution=0
WATCH_TICK i=40 now=2026-06-08T10:00:43+05:30 fut=402 opt=1987 features=96 decisions=2801 orders=0 risk=0 execution=0
WATCH_TICK i=41 now=2026-06-08T10:00:53+05:30 fut=407 opt=2006 features=98 decisions=2812 orders=0 risk=0 execution=0
WATCH_TICK i=42 now=2026-06-08T10:01:03+05:30 fut=410 opt=2027 features=100 decisions=2821 orders=0 risk=0 execution=0
WATCH_TICK i=43 now=2026-06-08T10:01:13+05:30 fut=413 opt=2046 features=102 decisions=2831 orders=0 risk=0 execution=0
WATCH_TICK i=44 now=2026-06-08T10:01:23+05:30 fut=417 opt=2062 features=104 decisions=2842 orders=0 risk=0 execution=0
WATCH_TICK i=45 now=2026-06-08T10:01:33+05:30 fut=419 opt=2083 features=106 decisions=2851 orders=0 risk=0 execution=0
WATCH_TICK i=46 now=2026-06-08T10:01:43+05:30 fut=421 opt=2099 features=108 decisions=2861 orders=0 risk=0 execution=0
WATCH_TICK i=47 now=2026-06-08T10:01:53+05:30 fut=424 opt=2118 features=110 decisions=2871 orders=0 risk=0 execution=0
WATCH_TICK i=48 now=2026-06-08T10:02:03+05:30 fut=428 opt=2138 features=112 decisions=2881 orders=0 risk=0 execution=0
WATCH_TICK i=49 now=2026-06-08T10:02:13+05:30 fut=433 opt=2155 features=114 decisions=2891 orders=0 risk=0 execution=0
WATCH_TICK i=50 now=2026-06-08T10:02:23+05:30 fut=434 opt=2176 features=116 decisions=2901 orders=0 risk=0 execution=0
WATCH_TICK i=51 now=2026-06-08T10:02:33+05:30 fut=438 opt=2194 features=119 decisions=2911 orders=0 risk=0 execution=0
WATCH_TICK i=52 now=2026-06-08T10:02:44+05:30 fut=438 opt=2214 features=121 decisions=2921 orders=0 risk=0 execution=0
WATCH_TICK i=53 now=2026-06-08T10:02:54+05:30 fut=442 opt=2232 features=123 decisions=2932 orders=0 risk=0 execution=0
WATCH_TICK i=54 now=2026-06-08T10:03:04+05:30 fut=445 opt=2253 features=125 decisions=2941 orders=0 risk=0 execution=0
WATCH_TICK i=55 now=2026-06-08T10:03:14+05:30 fut=0 opt=2 features=1 decisions=2950 orders=0 risk=0 execution=0
WATCH_TICK i=56 now=2026-06-08T10:03:24+05:30 fut=0 opt=2 features=1 decisions=2950 orders=0 risk=0 execution=0
WATCH_TICK i=57 now=2026-06-08T10:03:34+05:30 fut=0 opt=2 features=1 decisions=2950 orders=0 risk=0 execution=0
WATCH_TICK i=58 now=2026-06-08T10:03:44+05:30 fut=0 opt=2 features=1 decisions=2950 orders=0 risk=0 execution=0
WATCH_TICK i=59 now=2026-06-08T10:03:54+05:30 fut=1 opt=10 features=2 decisions=2955 orders=0 risk=0 execution=0
WATCH_TICK i=60 now=2026-06-08T10:04:04+05:30 fut=4 opt=29 features=5 decisions=2966 orders=0 risk=0 execution=0
WATCH_SECONDS=605

## Post-window pcheck
[2J[HScalpX MME live observer | now=2026-06-08 10:04:15 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:39785 ttl=24179ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=execution:mme-scalpx:39785 ttl=26068ms

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=OK service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4712ms message=-
health:features: status=OK service=features instance=features:mme-scalpx:39785 age=2.73s ttl=12271ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:39785 age=0.90s ttl=14110ms message=-
health:risk: status=WARN service=risk instance=risk:mme-scalpx:39785 age=2.50s ttl=7938ms message=CONTROLLED_PAPER_NOT_ARMED
health:execution: status=OK service=execution instance=execution:mme-scalpx:39785 age=3.36s ttl=6637ms message=-
health:monitor: status=OK service=monitor instance=monitor:mme-scalpx:39785 age=1.72s ttl=8326ms message=risk_blocks_entries,runtime_mode=live
health:provider:runtime: status=WARN service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4830ms message=-
health:zerodha:marketdata: status=OK service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4719ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4730ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4807ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4819ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:39785 age=1.47s ttl=4810ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-08 15:34:13 age=0.00s
frame_id=frame-1780893255205915146
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
future_json: symbol=NIFTY26JUNFUT ltp=23251.7 bid=23250.3 ask=23251.9 bid_qty_5=2145 ask_qty_5=845 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23251.9
ask_qty_5=845
bid=23250.3
bid_qty_5=2145
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780893255205915146
ltp=23251.7
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780913053000000000
ts_frame_ns=1780893255205915146

[state:snapshot:mme:opt:selected]
updated_at=2026-06-08 10:04:15 age=0.36s
frame_id=frame-1780893255205915146
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
ce_atm_json: symbol=NIFTY2660923200CE ltp=119.6 bid=119.2 ask=119.5 bid_qty_5=5980 ask_qty_5=6175 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=95.95 bid=95.6 ask=95.85 bid_qty_5=7995 ask_qty_5=5655 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=123.8 bid=123.85 ask=124.2 bid_qty_5=7605 ask_qty_5=11765 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=101.4 bid=100.65 ask=100.9 bid_qty_5=7475 ask_qty_5=7670 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780893255205915146

[state:snapshot:mme:fut:active]
updated_at=2026-06-08 15:34:13 age=0.00s
frame_id=frame-1780893255205915146
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
future_json: symbol=NIFTY26JUNFUT ltp=23251.7 bid=23250.3 ask=23251.9 bid_qty_5=2145 ask_qty_5=845 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23251.9
ask_qty_5=845
bid=23250.3
bid_qty_5=2145
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780893255205915146
ltp=23251.7
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780913053000000000
ts_frame_ns=1780893255205915146

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-08 10:04:15 age=0.36s
frame_id=frame-1780893255205915146
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=OK
validity_reason=ok
sync_ok=1
ts_span_ms=2000
ce_atm_json: symbol=NIFTY2660923200CE ltp=119.6 bid=119.2 ask=119.5 bid_qty_5=5980 ask_qty_5=6175 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=95.95 bid=95.6 ask=95.85 bid_qty_5=7995 ask_qty_5=5655 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=123.8 bid=123.85 ask=124.2 bid_qty_5=7605 ask_qty_5=11765 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=101.4 bid=100.65 ask=100.9 bid_qty_5=7475 ask_qty_5=7670 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780893255205915146

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-08 15:34:13 age=0.00s
frame_id=frame-1780893253639853045
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=2000
sync_ok=0
ts_span_ms=2000
future_json: symbol=NIFTY26JUNFUT ltp=23251.7 bid=23250.3 ask=23251.9 bid_qty_5=2145 ask_qty_5=845 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23251.9
ask_qty_5=845
bid=23250.3
bid_qty_5=2145
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780893253639853045
ltp=23251.7
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780913053000000000
ts_frame_ns=1780893253639853045

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-08 10:04:15 age=0.33s
frame_id=frame-1780893255239921039
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=2000
sync_ok=0
ts_span_ms=2000
ce_atm_json: symbol=NIFTY2660923200CE ltp=119.6 bid=119.2 ask=119.5 bid_qty_5=5980 ask_qty_5=6175 age_ms=0 validity=OK strike=23200.0
ce_atm1_json: symbol=NIFTY2660923250CE ltp=95.95 bid=95.6 ask=95.85 bid_qty_5=7995 ask_qty_5=5655 age_ms=0 validity=OK strike=23250.0
pe_atm_json: symbol=NIFTY2660923200PE ltp=123.8 bid=123.85 ask=124.2 bid_qty_5=7605 ask_qty_5=11765 age_ms=0 validity=OK strike=23200.0
pe_atm1_json: symbol=NIFTY2660923150PE ltp=101.4 bid=100.65 ask=100.9 bid_qty_5=7475 ask_qty_5=7670 age_ms=0 validity=OK strike=23150.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780893255239921039

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-08 10:04:15 age=0.36s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=ZERODHA
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=76
execution_fallback_status=DISABLED
execution_primary_status=HEALTHY
failover_active=True
futures_marketdata_status=HEALTHY
last_update_ns=1780893255205915146
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=FAILOVER_ACTIVE
ts_event_ns=1780893255205915146

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-06-08 10:04:12 age=2.67s
frame_id=features-1780893252945670889
feature_state_json: {"frame_id":"features-1780893252945670889","frame_ts_ns":1780893252945670889,"frame_valid":true,"warmup_complete":true,"regime":"FAST","selected_option":{"side":"CALL","ltp":124.35,"spread":0.29999999999999716,"spread_ratio":0.0024203307785397106,"depth_total":1365,"depth_ok":true,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":-1.75,"response_efficiency":11.666666666666224,"tradability_ok":true,"instrument_key":"NFO:NIFTY2660923200PE","instrument_token":"10824962","optio...
family_frames_json: {"mist_call":{"frame_id":"mist_call-1780893252945670889","frame_ts_ns":1780893252945670889,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"10824706","instrument_token":"10824706","option_symbol":"NIFTY2660923200CE","strike":23200.0,"option_price":119.2,"tick_size":0.05,"target_points"...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1780893252945670889,"frame_id":"features-1780893252945670889","frame_ts_ns":1780893252945670889,"ts_event_ns":1780893252945670889,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1780893252945670912,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1780893252945670889
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1780893252945670889
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-08 10:04:12 age=2.79s
family_features_version=1.1
frame_ts_ns=1780893252945670889
regime=FAST

[state:option:confirm]
updated_at=2026-06-08 10:04:12 age=2.79s
frame_ts_ns=1780893252945670889

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780893253583-0 | ts=2026-06-08 15:34:13 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23251.7 | bid=23250.3 | ask=23251.9
id=1780893248946-0 | ts=2026-06-08 15:34:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23250.0 | bid=23251.0 | ask=23252.9

[ticks:mme:opt:stream]
id=1780893255211-0 | ts=2026-06-08 15:34:13 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200CE | instrument_token=10824706 | trading_symbol=NIFTY2660923200CE | instrument_role=CE_ATM | ltp=119.6 | bid=119.2 | ask=119.5
id=1780893254793-0 | ts=2026-06-08 15:34:13 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200PE | instrument_token=10824962 | trading_symbol=NIFTY2660923200PE | instrument_role=PE_ATM | ltp=123.8 | bid=123.85 | ask=124.2

[features:mme:stream]
id=1780893253495-0 | ts=2026-06-08 10:04:12 | age=2.80s | frame_id=features-1780893252945670889
id=1780893248926-0 | ts=2026-06-08 10:04:08 | age=7.28s | frame_id=features-1780893248466187654

[system:health:stream]
id=1780893255340-0 | ts=2026-06-08 10:04:15 | age=0.43s | service_name=feeds | instance_id=feeds:mme-scalpx:39785 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1780893254892-0 | ts=2026-06-08 10:04:14 | age=0.85s | service_name=feeds | instance_id=feeds:mme-scalpx:39785 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1780893193292-0 | ts=2026-06-08 10:03:12 | age=63.52s | service_name=risk | instance_id=risk:mme-scalpx:37464 | event_type=risk_pending_claim_error | detail=cmd:mme:stream:ResponseError:NOGROUP No such key 'cmd:mme...
id=1780893193208-0 | ts=2026-06-08 10:03:13 | age=62.56s | instance_id=strategy:mme-scalpx:37464 | error_type=StrategyBridgeError

[ticks:mme:fut:zerodha:stream]
id=1780893253570-0 | ts=2026-06-08 15:34:13 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23251.7 | bid=23250.3 | ask=23251.9
id=1780893248940-0 | ts=2026-06-08 15:34:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23250.0 | bid=23251.0 | ask=23252.9

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780893255207-0 | ts=2026-06-08 15:34:13 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200CE | instrument_token=10824706 | trading_symbol=NIFTY2660923200CE | instrument_role=CE_ATM | ltp=119.6 | bid=119.2 | ask=119.5
id=1780893254779-0 | ts=2026-06-08 15:34:13 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923200PE | instrument_token=10824962 | trading_symbol=NIFTY2660923200PE | instrument_role=PE_ATM | ltp=123.8 | bid=123.85 | ask=124.2

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780893255290-0 | ts=2026-06-08 10:04:15 | age=0.55s | family_runtime_mode=OBSERVE_ONLY
id=1780893254885-0 | ts=2026-06-08 10:04:14 | age=0.97s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1780893193292-0 | ts=2026-06-08 10:03:12 | age=63.53s | service_name=risk | instance_id=risk:mme-scalpx:37464 | event_type=risk_pending_claim_error | detail=cmd:mme:stream:ResponseError:NOGROUP No such key 'cmd:mme...
id=1780893193208-0 | ts=2026-06-08 10:03:13 | age=62.57s | instance_id=strategy:mme-scalpx:37464 | error_type=StrategyBridgeError
id=1780893192967-0 | ts=2026-06-08 10:03:12 | age=62.80s | service_name=monitor | event_type=system_error

## Candidate / blocker audit from latest decision stream
{
  "actions": {
    "HOLD": 500
  },
  "candidate_positive": false,
  "data_valid_true_count": 397,
  "decision_rows_sampled": 500,
  "family_ids": {},
  "feature_rows_sampled": 7,
  "hold_only_false_count": 0,
  "latest_action": "HOLD",
  "latest_data_valid": "0",
  "latest_decision_id": "1780893254640-0",
  "latest_hold_only": "1",
  "latest_provider_ready_classic": "0",
  "latest_reason": "hold_only_family_features_consumer_bridge",
  "latest_safe_to_consume": "1",
  "max_activation_candidate_count": 0,
  "max_activation_selected_score": 0.0,
  "non_hold_count": 0,
  "provider_ready_classic_true_count": 415,
  "safe_to_consume_true_count": 500,
  "top_reasons": {
    "hold_only_family_features_consumer_bridge": 500
  }
}
AUDIT_RC=0

## Safety after window
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=PASS_R31E_NO_CANDIDATE_YET_CONTINUE_OBSERVE_ONLY_LONGER_WINDOW
