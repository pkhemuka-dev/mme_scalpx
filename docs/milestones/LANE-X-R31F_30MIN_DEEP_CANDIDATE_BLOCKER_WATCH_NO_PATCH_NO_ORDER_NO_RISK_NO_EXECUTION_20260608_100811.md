# LANE-X-R31F_30MIN_DEEP_CANDIDATE_BLOCKER_WATCH_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_100811
2026-06-08T10:08:11+05:30

LAW=DEEP_WATCH_ONLY_NO_PATCH_NO_START_NO_STOP_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## Prior R31E proof
R31E=run/proofs/LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_095409.json
{
  "tag": "LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_095409",
  "classification": "PASS_R31E_NO_CANDIDATE_YET_CONTINUE_OBSERVE_ONLY_LONGER_WINDOW",
  "patch_applied": false,
  "started_runtime": false,
  "stopped_runtime": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "report": "run/audits/LANE-X-R31E_10MIN_CANDIDATE_WATCH_WINDOW_NO_PATCH_NO_ORDER_NO_RISK_NO_EXECUTION_20260608_095409_report.md"
}

## Safety before 30-min watch
39947 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
orders_stream_len_before=0
risk_stream_len_before=0
execution_stream_len_before=0
fut_zerodha_before=70
opt_selected_zerodha_before=462
features_before=53
decisions_before=3198

## 30-minute observe-only deep watch begins
WATCH_TICK i=1 now=2026-06-08T10:08:11+05:30 fut=70 opt=462 features=53 decisions=3199 orders=0 risk=0 execution=0
WATCH_TICK i=2 now=2026-06-08T10:08:31+05:30 fut=76 opt=497 features=57 decisions=3218 orders=0 risk=0 execution=0
WATCH_TICK i=3 now=2026-06-08T10:08:51+05:30 fut=82 opt=539 features=61 decisions=3238 orders=0 risk=0 execution=0
WATCH_TICK i=4 now=2026-06-08T10:09:11+05:30 fut=88 opt=583 features=65 decisions=3258 orders=0 risk=0 execution=0
WATCH_TICK i=5 now=2026-06-08T10:09:31+05:30 fut=95 opt=621 features=70 decisions=3278 orders=0 risk=0 execution=0
WATCH_TICK i=6 now=2026-06-08T10:09:51+05:30 fut=102 opt=659 features=74 decisions=3300 orders=0 risk=0 execution=0
WATCH_TICK i=7 now=2026-06-08T10:10:11+05:30 fut=109 opt=693 features=78 decisions=3319 orders=0 risk=0 execution=0
WATCH_TICK i=8 now=2026-06-08T10:10:31+05:30 fut=115 opt=732 features=83 decisions=3340 orders=0 risk=0 execution=0
WATCH_TICK i=9 now=2026-06-08T10:10:51+05:30 fut=122 opt=765 features=86 decisions=3360 orders=0 risk=0 execution=0
WATCH_TICK i=10 now=2026-06-08T10:11:11+05:30 fut=127 opt=802 features=90 decisions=3380 orders=0 risk=0 execution=0
WATCH_TICK i=11 now=2026-06-08T10:11:31+05:30 fut=134 opt=841 features=94 decisions=3400 orders=0 risk=0 execution=0
WATCH_TICK i=12 now=2026-06-08T10:11:51+05:30 fut=136 opt=855 features=1 decisions=3410 orders=0 risk=0 execution=0
WATCH_TICK i=13 now=2026-06-08T10:12:12+05:30 fut=139 opt=877 features=4 decisions=3422 orders=0 risk=0 execution=0
WATCH_TICK i=14 now=2026-06-08T10:12:32+05:30 fut=143 opt=913 features=8 decisions=3440 orders=0 risk=0 execution=0
WATCH_TICK i=15 now=2026-06-08T10:12:52+05:30 fut=0 opt=0 features=1 decisions=3452 orders=0 risk=0 execution=0
WATCH_TICK i=16 now=2026-06-08T10:13:12+05:30 fut=1 opt=14 features=3 decisions=3460 orders=0 risk=0 execution=0
WATCH_TICK i=17 now=2026-06-08T10:13:32+05:30 fut=9 opt=54 features=8 decisions=3483 orders=0 risk=0 execution=0
WATCH_TICK i=18 now=2026-06-08T10:13:52+05:30 fut=13 opt=97 features=12 decisions=3504 orders=0 risk=0 execution=0
WATCH_TICK i=19 now=2026-06-08T10:14:12+05:30 fut=16 opt=123 features=14 decisions=3519 orders=0 risk=0 execution=0
WATCH_TICK i=20 now=2026-06-08T10:14:32+05:30 fut=18 opt=155 features=17 decisions=3536 orders=0 risk=0 execution=0
WATCH_TICK i=21 now=2026-06-08T10:14:52+05:30 fut=23 opt=194 features=21 decisions=3555 orders=0 risk=0 execution=0
WATCH_TICK i=22 now=2026-06-08T10:15:12+05:30 fut=28 opt=238 features=26 decisions=3577 orders=0 risk=0 execution=0
WATCH_TICK i=23 now=2026-06-08T10:15:32+05:30 fut=0 opt=2 features=0 decisions=3584 orders=0 risk=0 execution=0
WATCH_TICK i=24 now=2026-06-08T10:15:53+05:30 fut=4 opt=25 features=4 decisions=3601 orders=0 risk=0 execution=0
WATCH_TICK i=25 now=2026-06-08T10:16:13+05:30 fut=10 opt=62 features=8 decisions=3622 orders=0 risk=0 execution=0
WATCH_TICK i=26 now=2026-06-08T10:16:33+05:30 fut=2 opt=98 features=13 decisions=3644 orders=0 risk=0 execution=0
WATCH_TICK i=27 now=2026-06-08T10:16:53+05:30 fut=0 opt=1 features=0 decisions=3650 orders=0 risk=0 execution=0
WATCH_TICK i=28 now=2026-06-08T10:17:13+05:30 fut=0 opt=0 features=0 decisions=0 orders=0 risk=0 execution=0
WATCH_TICK i=29 now=2026-06-08T10:17:33+05:30 fut=0 opt=0 features=1 decisions=0 orders=0 risk=0 execution=0
WATCH_TICK i=30 now=2026-06-08T10:17:53+05:30 fut=9 opt=39 features=6 decisions=20 orders=0 risk=0 execution=0
WATCH_TICK i=31 now=2026-06-08T10:18:13+05:30 fut=19 opt=74 features=10 decisions=42 orders=0 risk=0 execution=0
WATCH_TICK i=32 now=2026-06-08T10:18:33+05:30 fut=24 opt=118 features=15 decisions=65 orders=0 risk=0 execution=0
WATCH_TICK i=33 now=2026-06-08T10:18:53+05:30 fut=32 opt=154 features=19 decisions=86 orders=0 risk=0 execution=0
WATCH_TICK i=34 now=2026-06-08T10:19:13+05:30 fut=40 opt=190 features=23 decisions=107 orders=0 risk=0 execution=0
WATCH_TICK i=35 now=2026-06-08T10:19:33+05:30 fut=44 opt=230 features=28 decisions=127 orders=0 risk=0 execution=0
WATCH_TICK i=36 now=2026-06-08T10:19:54+05:30 fut=48 opt=266 features=32 decisions=147 orders=0 risk=0 execution=0
WATCH_TICK i=37 now=2026-06-08T10:20:14+05:30 fut=56 opt=303 features=36 decisions=168 orders=0 risk=0 execution=0
WATCH_TICK i=38 now=2026-06-08T10:20:34+05:30 fut=60 opt=342 features=41 decisions=188 orders=0 risk=0 execution=0
WATCH_TICK i=39 now=2026-06-08T10:20:54+05:30 fut=66 opt=378 features=45 decisions=209 orders=0 risk=0 execution=0
WATCH_TICK i=40 now=2026-06-08T10:21:14+05:30 fut=72 opt=412 features=49 decisions=228 orders=0 risk=0 execution=0
WATCH_TICK i=41 now=2026-06-08T10:21:34+05:30 fut=81 opt=445 features=53 decisions=249 orders=0 risk=0 execution=0
WATCH_TICK i=42 now=2026-06-08T10:21:54+05:30 fut=88 opt=483 features=57 decisions=269 orders=0 risk=0 execution=0
WATCH_TICK i=43 now=2026-06-08T10:22:14+05:30 fut=92 opt=524 features=61 decisions=289 orders=0 risk=0 execution=0
WATCH_TICK i=44 now=2026-06-08T10:22:34+05:30 fut=97 opt=563 features=65 decisions=309 orders=0 risk=0 execution=0
WATCH_TICK i=45 now=2026-06-08T10:22:54+05:30 fut=105 opt=596 features=69 decisions=330 orders=0 risk=0 execution=0
WATCH_TICK i=46 now=2026-06-08T10:23:14+05:30 fut=112 opt=633 features=73 decisions=350 orders=0 risk=0 execution=0
WATCH_TICK i=47 now=2026-06-08T10:23:35+05:30 fut=121 opt=668 features=77 decisions=369 orders=0 risk=0 execution=0
WATCH_TICK i=48 now=2026-06-08T10:23:55+05:30 fut=126 opt=702 features=81 decisions=390 orders=0 risk=0 execution=0
WATCH_TICK i=49 now=2026-06-08T10:24:15+05:30 fut=131 opt=738 features=85 decisions=410 orders=0 risk=0 execution=0
WATCH_TICK i=50 now=2026-06-08T10:24:35+05:30 fut=135 opt=764 features=88 decisions=426 orders=0 risk=0 execution=0
WATCH_TICK i=51 now=2026-06-08T10:24:55+05:30 fut=141 opt=782 features=89 decisions=438 orders=0 risk=0 execution=0
WATCH_TICK i=52 now=2026-06-08T10:25:15+05:30 fut=145 opt=815 features=93 decisions=457 orders=0 risk=0 execution=0
WATCH_TICK i=53 now=2026-06-08T10:25:35+05:30 fut=151 opt=852 features=97 decisions=476 orders=0 risk=0 execution=0
WATCH_TICK i=54 now=2026-06-08T10:25:55+05:30 fut=157 opt=887 features=100 decisions=496 orders=0 risk=0 execution=0
WATCH_TICK i=55 now=2026-06-08T10:26:16+05:30 fut=160 opt=919 features=104 decisions=515 orders=0 risk=0 execution=0
WATCH_TICK i=56 now=2026-06-08T10:26:36+05:30 fut=167 opt=952 features=108 decisions=534 orders=0 risk=0 execution=0
WATCH_TICK i=57 now=2026-06-08T10:26:56+05:30 fut=174 opt=991 features=112 decisions=554 orders=0 risk=0 execution=0
WATCH_TICK i=58 now=2026-06-08T10:27:16+05:30 fut=182 opt=1025 features=116 decisions=576 orders=0 risk=0 execution=0
WATCH_TICK i=59 now=2026-06-08T10:27:36+05:30 fut=191 opt=1054 features=119 decisions=595 orders=0 risk=0 execution=0
WATCH_TICK i=60 now=2026-06-08T10:27:56+05:30 fut=194 opt=1089 features=123 decisions=616 orders=0 risk=0 execution=0
WATCH_TICK i=61 now=2026-06-08T10:28:16+05:30 fut=197 opt=1125 features=127 decisions=636 orders=0 risk=0 execution=0
WATCH_TICK i=62 now=2026-06-08T10:28:36+05:30 fut=204 opt=1160 features=130 decisions=655 orders=0 risk=0 execution=0
WATCH_TICK i=63 now=2026-06-08T10:28:56+05:30 fut=212 opt=1191 features=134 decisions=674 orders=0 risk=0 execution=0
WATCH_TICK i=64 now=2026-06-08T10:29:16+05:30 fut=222 opt=1227 features=138 decisions=694 orders=0 risk=0 execution=0
WATCH_TICK i=65 now=2026-06-08T10:29:36+05:30 fut=228 opt=1260 features=141 decisions=713 orders=0 risk=0 execution=0
WATCH_TICK i=66 now=2026-06-08T10:29:57+05:30 fut=235 opt=1287 features=145 decisions=732 orders=0 risk=0 execution=0
WATCH_TICK i=67 now=2026-06-08T10:30:17+05:30 fut=240 opt=1325 features=149 decisions=753 orders=0 risk=0 execution=0
WATCH_TICK i=68 now=2026-06-08T10:30:37+05:30 fut=244 opt=1360 features=153 decisions=772 orders=0 risk=0 execution=0
WATCH_TICK i=69 now=2026-06-08T10:30:57+05:30 fut=252 opt=1397 features=157 decisions=790 orders=0 risk=0 execution=0
WATCH_TICK i=70 now=2026-06-08T10:31:17+05:30 fut=253 opt=1431 features=160 decisions=808 orders=0 risk=0 execution=0
WATCH_TICK i=71 now=2026-06-08T10:31:37+05:30 fut=258 opt=1472 features=164 decisions=826 orders=0 risk=0 execution=0
WATCH_TICK i=72 now=2026-06-08T10:31:57+05:30 fut=261 opt=1507 features=168 decisions=845 orders=0 risk=0 execution=0
WATCH_TICK i=73 now=2026-06-08T10:32:17+05:30 fut=267 opt=1539 features=172 decisions=865 orders=0 risk=0 execution=0
WATCH_TICK i=74 now=2026-06-08T10:32:37+05:30 fut=271 opt=1574 features=175 decisions=884 orders=0 risk=0 execution=0
WATCH_TICK i=75 now=2026-06-08T10:32:57+05:30 fut=278 opt=1606 features=179 decisions=903 orders=0 risk=0 execution=0
WATCH_TICK i=76 now=2026-06-08T10:33:17+05:30 fut=284 opt=1641 features=183 decisions=923 orders=0 risk=0 execution=0
WATCH_TICK i=77 now=2026-06-08T10:33:37+05:30 fut=293 opt=1673 features=187 decisions=941 orders=0 risk=0 execution=0
WATCH_TICK i=78 now=2026-06-08T10:33:58+05:30 fut=302 opt=1704 features=191 decisions=960 orders=0 risk=0 execution=0
WATCH_TICK i=79 now=2026-06-08T10:34:18+05:30 fut=312 opt=1739 features=195 decisions=980 orders=0 risk=0 execution=0
WATCH_TICK i=80 now=2026-06-08T10:34:38+05:30 fut=316 opt=1778 features=199 decisions=999 orders=0 risk=0 execution=0
WATCH_TICK i=81 now=2026-06-08T10:34:58+05:30 fut=323 opt=1814 features=203 decisions=1018 orders=0 risk=0 execution=0
WATCH_TICK i=82 now=2026-06-08T10:35:18+05:30 fut=325 opt=1827 features=204 decisions=1027 orders=0 risk=0 execution=0
WATCH_TICK i=83 now=2026-06-08T10:35:38+05:30 fut=331 opt=1847 features=206 decisions=1040 orders=0 risk=0 execution=0
WATCH_TICK i=84 now=2026-06-08T10:35:58+05:30 fut=339 opt=1877 features=210 decisions=1056 orders=0 risk=0 execution=0
WATCH_TICK i=85 now=2026-06-08T10:36:18+05:30 fut=344 opt=1911 features=214 decisions=1076 orders=0 risk=0 execution=0
WATCH_TICK i=86 now=2026-06-08T10:36:38+05:30 fut=352 opt=1949 features=218 decisions=1093 orders=0 risk=0 execution=0
WATCH_TICK i=87 now=2026-06-08T10:36:58+05:30 fut=358 opt=1988 features=222 decisions=1113 orders=0 risk=0 execution=0
WATCH_TICK i=88 now=2026-06-08T10:37:19+05:30 fut=366 opt=2021 features=226 decisions=1130 orders=0 risk=0 execution=0
WATCH_TICK i=89 now=2026-06-08T10:37:39+05:30 fut=371 opt=2060 features=230 decisions=1148 orders=0 risk=0 execution=0
WATCH_TICK i=90 now=2026-06-08T10:37:59+05:30 fut=379 opt=2092 features=234 decisions=1165 orders=0 risk=0 execution=0
WATCH_SECONDS=1808

## Post-window pcheck
[2J[HScalpX MME live observer | now=2026-06-08 10:38:20 | repo=/home/Lenovo/scalpx/projects/mme_scalpx | width=140

====================================================================================================
LOCKS
====================================================================================================
lock:feeds: owner=feeds:mme-scalpx:42167 ttl=22109ms
lock:strategy: owner=- ttl=missing
lock:execution: owner=execution:mme-scalpx:42167 ttl=25502ms

====================================================================================================
HEARTBEATS
====================================================================================================
health:feeds: status=OK service=feeds instance=feeds:mme-scalpx:42167 age=1.53s ttl=4523ms message=-
health:features: status=OK service=features instance=features:mme-scalpx:42167 age=3.10s ttl=11915ms message=-
health:strategy: status=OK service=strategy instance=strategy:mme-scalpx:42167 age=1.61s ttl=13398ms message=-
health:risk: status=WARN service=risk instance=risk:mme-scalpx:42167 age=1.26s ttl=9889ms message=CONTROLLED_PAPER_NOT_ARMED
health:execution: status=OK service=execution instance=execution:mme-scalpx:42167 age=3.19s ttl=6814ms message=-
health:monitor: status=WARN service=monitor instance=monitor:mme-scalpx:42167 age=2.85s ttl=7159ms message=report:missing_heartbeat,runtime_mode=live
health:provider:runtime: status=WARN service=feeds instance=feeds:mme-scalpx:42167 age=1.54s ttl=4843ms message=-
health:zerodha:marketdata: status=OK service=feeds instance=feeds:mme-scalpx:42167 age=1.54s ttl=4541ms message=-
health:zerodha:execution: status=OK service=feeds instance=feeds:mme-scalpx:42167 age=1.54s ttl=4624ms message=-
health:dhan:marketdata: status=ERROR service=feeds instance=feeds:mme-scalpx:42167 age=1.54s ttl=4627ms message=-
health:dhan:execution: status=OK service=feeds instance=feeds:mme-scalpx:42167 age=1.54s ttl=4732ms message=-
health:dhan:auth: status=OK service=feeds instance=feeds:mme-scalpx:42167 age=1.54s ttl=4720ms message=-

====================================================================================================
SNAPSHOT HASHES (feeds.py outputs)
====================================================================================================

[state:snapshot:mme:fut]
updated_at=2026-06-08 16:08:17 age=0.00s
frame_id=frame-1780895299493695538
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=12000
sync_ok=0
ts_span_ms=12000
future_json: symbol=NIFTY26JUNFUT ltp=23264.8 bid=23262.9 ask=23269.0 bid_qty_5=1105 ask_qty_5=1495 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23269.0
ask_qty_5=1495
bid=23262.9
bid_qty_5=1105
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780895299493695538
ltp=23264.8
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780915097000000000
ts_frame_ns=1780895299493695538

[state:snapshot:mme:opt:selected]
updated_at=2026-06-08 10:38:19 age=0.83s
frame_id=frame-1780895299493695538
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=12000
sync_ok=0
ts_span_ms=12000
ce_atm_json: symbol=NIFTY2660923150CE ltp=162.25 bid=161.95 ask=162.25 bid_qty_5=2210 ask_qty_5=5590 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=133.15 bid=133.0 ask=133.4 bid_qty_5=7865 ask_qty_5=5525 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=89.25 bid=89.05 ask=89.25 bid_qty_5=8190 ask_qty_5=11895 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=70.15 bid=69.95 ask=70.1 bid_qty_5=22620 ask_qty_5=16705 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780895299493695538

[state:snapshot:mme:fut:active]
updated_at=2026-06-08 16:08:17 age=0.00s
frame_id=frame-1780895299493695538
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=12000
sync_ok=0
ts_span_ms=12000
future_json: symbol=NIFTY26JUNFUT ltp=23264.8 bid=23262.9 ask=23269.0 bid_qty_5=1105 ask_qty_5=1495 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23269.0
ask_qty_5=1495
bid=23262.9
bid_qty_5=1105
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780895299493695538
ltp=23264.8
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780915097000000000
ts_frame_ns=1780895299493695538

[state:snapshot:mme:opt:selected:active]
updated_at=2026-06-08 10:38:19 age=0.83s
frame_id=frame-1780895299493695538
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=12000
sync_ok=0
ts_span_ms=12000
ce_atm_json: symbol=NIFTY2660923150CE ltp=162.25 bid=161.95 ask=162.25 bid_qty_5=2210 ask_qty_5=5590 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=133.15 bid=133.0 ask=133.4 bid_qty_5=7865 ask_qty_5=5525 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=89.25 bid=89.05 ask=89.25 bid_qty_5=8190 ask_qty_5=11895 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=70.15 bid=69.95 ask=70.1 bid_qty_5=22620 ask_qty_5=16705 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780895299493695538

[state:snapshot:mme:fut:zerodha]
updated_at=2026-06-08 16:08:17 age=0.00s
frame_id=frame-1780895298383307825
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=11000
sync_ok=0
ts_span_ms=11000
future_json: symbol=NIFTY26JUNFUT ltp=23264.8 bid=23262.9 ask=23269.0 bid_qty_5=1105 ask_qty_5=1495 age_ms=0 validity=OK strike=0.0
stale_mask_json: []
ask=23269.0
ask_qty_5=1495
bid=23262.9
bid_qty_5=1105
instrument_key=NFO:NIFTY26JUNFUT
instrument_token=15956226
is_active_provider_snapshot=True
last_update_ns=1780895298383307825
ltp=23264.8
provider_role=futures_marketdata
tick_validity=OK
trading_symbol=NIFTY26JUNFUT
ts_event_ns=1780915097000000000
ts_frame_ns=1780895298383307825

[state:snapshot:mme:fut:dhan]
MISSING

[state:snapshot:mme:opt:selected:zerodha]
updated_at=2026-06-08 10:38:20 age=0.09s
frame_id=frame-1780895300239849481
selection_version=mme-instruments-v1
provider_id=ZERODHA
validity=UNSYNCED
validity_reason=unsynced:span_ms=12000
sync_ok=0
ts_span_ms=12000
ce_atm_json: symbol=NIFTY2660923150CE ltp=162.3 bid=162.0 ask=162.4 bid_qty_5=4615 ask_qty_5=4875 age_ms=0 validity=OK strike=23150.0
ce_atm1_json: symbol=NIFTY2660923200CE ltp=133.15 bid=133.0 ask=133.4 bid_qty_5=7865 ask_qty_5=5525 age_ms=0 validity=OK strike=23200.0
pe_atm_json: symbol=NIFTY2660923150PE ltp=89.25 bid=89.05 ask=89.25 bid_qty_5=8190 ask_qty_5=11895 age_ms=0 validity=OK strike=23150.0
pe_atm1_json: symbol=NIFTY2660923100PE ltp=70.15 bid=69.95 ask=70.1 bid_qty_5=22620 ask_qty_5=16705 age_ms=0 validity=OK strike=23100.0
stale_mask_json: []
is_active_provider_snapshot=1
ts_frame_ns=1780895300239849481

[state:snapshot:mme:opt:selected:dhan]
MISSING

[state:context:mme:dhan]
MISSING

[state:provider:runtime]
updated_at=2026-06-08 10:38:20 age=0.21s
futures_marketdata_provider_id=ZERODHA
selected_option_marketdata_provider_id=ZERODHA
option_context_provider_id=DHAN
execution_primary_provider_id=ZERODHA
execution_fallback_provider_id=DHAN
family_runtime_mode=OBSERVE_ONLY
failover_mode=MANUAL
override_mode=AUTO
transition_reason=BOOTSTRAP
provider_transition_seq=3584
execution_fallback_status=DISABLED
execution_primary_status=HEALTHY
failover_active=True
futures_marketdata_status=HEALTHY
last_update_ns=1780895300121266665
message=Dhan execution fallback disabled until concrete Dhan execution transport is implemented and proof-enabled
option_context_status=UNAVAILABLE
pending_failover=False
selected_option_marketdata_status=FAILOVER_ACTIVE
ts_event_ns=1780895300121266665

====================================================================================================
FEATURE HASHES (features.py outputs)
====================================================================================================

[state:features:mme:fut]
updated_at=2026-06-08 10:38:17 age=3.00s
frame_id=features-1780895297361354414
feature_state_json: {"frame_id":"features-1780895297361354414","frame_ts_ns":1780895297361354414,"frame_valid":true,"warmup_complete":true,"regime":"FAST","selected_option":{"side":"CALL","ltp":162.25,"spread":0.30000000000001137,"spread_ratio":0.0018524235875270849,"depth_total":1690,"depth_ok":true,"ofi_ratio_proxy":null,"microprice":null,"micro_edge":null,"delta_3":-0.5,"response_efficiency":1.111111111111069,"tradability_ok":true,"instrument_key":"NFO:NIFTY2660923150CE","instrument_token":"10823170","option_...
family_frames_json: {"mist_call":{"frame_id":"mist_call-1780895297361354414","frame_ts_ns":1780895297361354414,"family_id":"MIST","branch_id":"CALL","side":"CALL","runtime_mode":"NORMAL","family_runtime_mode":"OBSERVE_ONLY","active_futures_provider_id":"ZERODHA","active_selected_option_provider_id":"ZERODHA","active_option_context_provider_id":"DHAN","instrument_key":"10823170","instrument_token":"10823170","option_symbol":"NIFTY2660923150CE","strike":23150.0,"option_price":162.0,"tick_size":0.05,"target_points"...
payload_json: {"schema_version":1,"service":"features","generated_at_ns":1780895297361354414,"frame_id":"features-1780895297361354414","frame_ts_ns":1780895297361354414,"ts_event_ns":1780895297361354414,"frame_valid":true,"warmup_complete":true,"family_features":{"schema_version":1,"service":"features","family_features_version":"1.1","generated_at_ns":1780895297361354496,"snapshot":{"valid":true,"validity":"OK","sync_ok":false,"freshness_ok":true,"packet_gap_ok":true,"warmup_ok":true,"active_snapshot_ns":1...
family_features_version=1.1
frame_ts_ns=1780895297361354414
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1780895297361354414
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-08 10:38:17 age=3.10s
family_features_version=1.1
frame_ts_ns=1780895297361354414
regime=FAST

[state:option:confirm]
updated_at=2026-06-08 10:38:17 age=3.10s
frame_ts_ns=1780895297361354414

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1780895298371-0 | ts=2026-06-08 16:08:17 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23264.8 | bid=23262.9 | ask=23269.0
id=1780895290788-0 | ts=2026-06-08 16:08:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23269.0 | bid=23265.1 | ask=23269.0

[ticks:mme:opt:stream]
id=1780895300220-0 | ts=2026-06-08 16:08:18 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150CE | instrument_token=10823170 | trading_symbol=NIFTY2660923150CE | instrument_role=CE_ATM | ltp=162.3 | bid=162.0 | ask=162.4
id=1780895299507-0 | ts=2026-06-08 16:08:18 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150PE | instrument_token=10823426 | trading_symbol=NIFTY2660923150PE | instrument_role=PE_ATM | ltp=89.25 | bid=89.05 | ask=89.25

[features:mme:stream]
id=1780895297910-0 | ts=2026-06-08 10:38:17 | age=3.11s | frame_id=features-1780895297361354414
id=1780895293273-0 | ts=2026-06-08 10:38:12 | age=7.90s | frame_id=features-1780895292570083373

[system:health:stream]
id=1780895300335-0 | ts=2026-06-08 10:38:19 | age=1.20s | service_name=monitor | event_type=system_diagnostics
id=1780895300327-0 | ts=2026-06-08 10:38:20 | age=0.16s | service_name=feeds | instance_id=feeds:mme-scalpx:42167 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1780894486439-0 | ts=2026-06-08 10:24:45 | age=815.09s | service_name=monitor | event_type=system_error
id=1780894056216-0 | ts=2026-06-08 10:17:36 | age=1244.31s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError

[ticks:mme:fut:zerodha:stream]
id=1780895298307-0 | ts=2026-06-08 16:08:17 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23264.8 | bid=23262.9 | ask=23269.0
id=1780895290787-0 | ts=2026-06-08 16:08:08 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23269.0 | bid=23265.1 | ask=23269.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1780895300123-0 | ts=2026-06-08 16:08:18 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150CE | instrument_token=10823170 | trading_symbol=NIFTY2660923150CE | instrument_role=CE_ATM | ltp=162.3 | bid=162.0 | ask=162.4
id=1780895299495-0 | ts=2026-06-08 16:08:18 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2660923150PE | instrument_token=10823426 | trading_symbol=NIFTY2660923150PE | instrument_role=PE_ATM | ltp=89.25 | bid=89.05 | ask=89.25

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1780895300261-0 | ts=2026-06-08 10:38:20 | age=0.41s | family_runtime_mode=OBSERVE_ONLY
id=1780895299620-0 | ts=2026-06-08 10:38:19 | age=1.03s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1780894486439-0 | ts=2026-06-08 10:24:45 | age=815.12s | service_name=monitor | event_type=system_error
id=1780894056216-0 | ts=2026-06-08 10:17:36 | age=1244.34s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894055709-0 | ts=2026-06-08 10:17:35 | age=1244.85s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894055155-0 | ts=2026-06-08 10:17:35 | age=1245.41s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894054515-0 | ts=2026-06-08 10:17:34 | age=1246.04s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894054050-0 | ts=2026-06-08 10:17:34 | age=1246.51s | instance_id=strategy:mme-scalpx:42167 | error_type=FeatureFamilyContractError
id=1780894033321-0 | ts=2026-06-08 10:17:13 | age=1267.46s | service_name=monitor | event_type=system_error
id=1780894033064-0 | ts=2026-06-08 10:17:12 | age=1268.33s | instance_id=execution:mme-scalpx:41936

## Deep candidate / blocker / family audit
{
  "actions": {
    "HOLD": 1184
  },
  "branch_ids": {},
  "candidate_positive": false,
  "candidate_rows_count": 0,
  "data_valid_true_count": 967,
  "decision_rows_sampled": 1184,
  "family_ids": {},
  "feature_rows_sampled": 239,
  "hold_only_false_count": 0,
  "latest_action": "HOLD",
  "latest_data_valid": "1",
  "latest_decision_id": "1780895299950-0",
  "latest_hold_only": "1",
  "latest_provider_ready_classic": "1",
  "latest_reason": "hold_only_family_features_consumer_bridge",
  "latest_safe_to_consume": "1",
  "max_activation_candidate_count": 0,
  "max_activation_selected_score": 0.0,
  "non_hold_count": 0,
  "provider_ready_classic_true_count": 991,
  "safe_to_consume_true_count": 1184,
  "surface_family_max_scores": {
    "MISB": 0.0,
    "MISC": 0.0,
    "MISO": 0.0,
    "MISR": 0.0,
    "MIST": 0.0
  },
  "surface_family_seen_counts": {
    "MISB": 717,
    "MISC": 717,
    "MISO": 717,
    "MISR": 717,
    "MIST": 717
  },
  "top_activation_reasons": {
    "no_candidate": 967,
    "view_data_invalid": 217
  },
  "top_reasons": {
    "hold_only_family_features_consumer_bridge": 1184
  },
  "top_surface_blockers": {
    "MISB:breakout_shelf_missing_reason=shelf_width_out_of_bounds": 3760,
    "MISB:failed_stage=futures_bias": 1744,
    "MISB:failed_stage=shelf_validation": 2064,
    "MISC:compression_missing_reason=compression_width_out_of_bounds": 2464,
    "MISC:failed_stage=compression_detection": 3808,
    "MISO:batch9_freeze_blocked_reason=runtime_disabled": 4780,
    "MISO:failed_stage=runtime_disabled": 4780,
    "MISO:futures_contradiction_blocked=False": 4780,
    "MISO:pre_batch9_failed_stage=strike_bundle_present": 4780,
    "MISO:queue_reload_blocked=False": 4780,
    "MISR:failed_stage=active_trap_zone_selection": 3808,
    "MIST:failed_stage=futures_bias": 1744,
    "MIST:failed_stage=futures_impulse": 2032,
    "MIST:micro_trap_blocked=True": 3824,
    "UNKNOWN:failover_active=True": 1428,
    "UNKNOWN:failover_mode=MANUAL": 1434,
    "UNKNOWN:pending_failover=False": 1434,
    "UNKNOWN:provider_runtime_blocked=False": 1428,
    "UNKNOWN:queue_reload_blocked=False": 5258,
    "UNKNOWN:regime_reason=fast_ratio_or_event_rate": 20928,
    "UNKNOWN:regime_reason=lowvol_ratio_event_rate_volume": 1344,
    "UNKNOWN:regime_reason=mid_band": 576,
    "UNKNOWN:transition_reason=BOOTSTRAP": 1434,
    "UNKNOWN:validity_reason=invalid_members:CE_ATM": 528,
    "UNKNOWN:validity_reason=invalid_members:CE_ATM1": 616,
    "UNKNOWN:validity_reason=invalid_members:FUTURES": 1848,
    "UNKNOWN:validity_reason=invalid_members:PE_ATM": 614,
    "UNKNOWN:validity_reason=ok": 13288,
    "UNKNOWN:validity_reason=unsynced:span_ms=6000": 880,
    "UNKNOWN:validity_reason=unsynced:span_ms=7000": 618
  }
}
AUDIT_RC=0

## Safety after window
orders_stream_len_after=0
risk_stream_len_after=0
execution_stream_len_after=0

CLASSIFICATION=PASS_R31F_NO_CANDIDATE_YET_DEEP_BLOCKER_MAP_READY
