# LANE-X-CONTROLLED-PAPER-R1B_CLEAN_SEMANTIC_PREFLIGHT_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_105550

## Proof

```json
{
  "base_live_keys": {
    "decisions:mme:stream": {
      "len": 2706,
      "tail": "family_id\": \"MISR\", \"is_blocked\": false, \"is_candidate\": false, \"owner_scope\": \"MISR|PUT\", \"priority\": 0.0, \"reason\": \"reversal_direction_not_confirmed\", \"score\": 0.0, \"side\": \"\"}, {\"action\": \"HOLD\", \"blocker\": \"{}\", \"branch_id\": \"CALL\", \"eligible\": false, \"family_id\": \"MISO\", \"is_blocked\": false, \"is_candidate\": false, \"owner_scope\": \"MISO|CALL\", \"priority\": 0.0, \"reason\": \"stage_provider_ready_miso_failed\", \"score\": 0.0, \"side\": \"\"}, {\"action\": \"HOLD\", \"blocker\": \"{}\", \"branch_id\": \"PUT\", \"eligible\": false, \"family_id\": \"MISO\", \"is_blocked\": false, \"is_candidate\": false, \"owner_scope\": \"MISO|PUT\", \"priority\": 0.0, \"reason\": \"stage_provider_ready_miso_failed\", \"score\": 0.0, \"side\": \"\"}], \"no_signal_count\": 9, \"projection_source\": \"activation_report_json\", \"reason\": \"candidate_observed_dry_run\", \"schema\": \"o23q_family_scope_candidates_v1\", \"selected\": {\"action\": \"ENTER_CALL\", \"blocker\": \"{}\", \"branch_id\": \"CALL\", \"eligible\": false, \"family_id\": \"MIST\", \"is_blocked\": false, \"is_candidate\": true, \"owner_scope\": \"MIST|CALL\", \"priority\": 67.0, \"reason\": \"mist_candidate_ready\", \"score\": 0.67, \"side\": \"\"}, \"strategy_report_only\": true}\no23q_r13_family_scope_candidates_projection_patch\n1\n",
      "type": "stream"
    },
    "features:mme:stream": {
      "len": 186,
      "tail": "t\":true,\"selected_option_present\":true,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall_distance_pts\":null,\"put_wall_distance_pts\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"oi_bias\":\"NEUTRAL\",\"cross_option_ready\":true},\"rich_surface\":true,\"futures_impulse_score\":1.0,\"breakout_score\":1.0,\"breakout_trigger_score\":1.0,\"pullback_resume_score\":0.18,\"resume_score\":0.18,\"option_confirmation_score\":1.0,\"option_response_score\":1.0,\"option_confirm_score\":1.0,\"r39we_dynamic_score_aliases\":{\"source\":\"existing_surface_fields_only\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"futures_impulse_score\":1.0,\"breakout_score\":1.0,\"pullback_resume_score\":0.18,\"option_confirmation_score\":1.0,\"thresholds_changed\":false,\"candidate_forced\":false}}}},\"mapping_repair\":{\"batch\":\"26-O16\",\"all_required_branch_keys\":[\"misb_call\",\"misb_put\",\"misc_call\",\"misc_put\",\"miso_call\",\"miso_put\",\"misr_call\",\"misr_put\",\"mist_call\",\"mist_put\"],\"missing_branch_keys\":[],\"branch_frame_count\":10,\"miso_provider_ready_truth_preserved\":false,\"no_doctrine_evaluation\":true,\"no_order_side_effect\":true,\"no_threshold_relaxation\":true}}\no23p_r6b_r3_family_payload_publish_patch\n1\n",
      "type": "stream"
    },
    "ticks:mme:fut:stream": {
      "len": 384,
      "tail": "1781587554094-0\ninstrument_key\nNFO:NIFTY26JUNFUT\ninstrument_role\nFUTURES\nts_event_ns\n1781607353000000000\nprovider_id\nZERODHA\nprovider_role\nfutures_marketdata\nexchange\nNFO\ninstrument_token\n15956226\ntrading_symbol\nNIFTY26JUNFUT\nts_provider_ns\n1781607353000000000\nts_recv_ns\n1781587554090766473\nseq_no\n\nltp\n23990.0\nlast_qty\n\nvolume\n0\noi\n\nbid\n23988.1\nask\n23990.0\nbid_qty\n325\nask_qty\n195\nbids\n[{\"price\":23988.1,\"quantity\":325,\"orders\":3},{\"price\":23984.1,\"quantity\":65,\"orders\":1},{\"price\":23982.0,\"quantity\":1495,\"orders\":1},{\"price\":23981.9,\"quantity\":65,\"orders\":1},{\"price\":23981.7,\"quantity\":65,\"orders\":1}]\nasks\n[{\"price\":23990.0,\"quantity\":195,\"orders\":1},{\"price\":23993.0,\"quantity\":390,\"orders\":3},{\"price\":23993.8,\"quantity\":65,\"orders\":1},{\"price\":23994.0,\"quantity\":650,\"orders\":3},{\"price\":23994.5,\"quantity\":195,\"orders\":1}]\noption_side\n\nstrike\n0.0\nexpiry\n2026-06-30\ntick_validity\nOK\nreject_reason\n\nis_selected_option\nFalse\nis_shadow_option\nFalse\n",
      "type": "stream"
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "len": 12928,
      "tail": "1781587557070-0\ninstrument_key\nNFO:NIFTY2661623850PE\ninstrument_role\nPE_ATM1\nts_event_ns\n1781607356000000000\nprovider_id\nZERODHA\nprovider_role\nselected_option_marketdata\nexchange\nNFO\ninstrument_token\n12956162\ntrading_symbol\nNIFTY2661623850PE\nts_provider_ns\n1781607356000000000\nts_recv_ns\n1781587557069260121\nseq_no\n\nltp\n8.7\nlast_qty\n\nvolume\n0\noi\n\nbid\n8.65\nask\n8.7\nbid_qty\n31265\nask_qty\n15665\nbids\n[{\"price\":8.65,\"quantity\":31265,\"orders\":34},{\"price\":8.6,\"quantity\":88205,\"orders\":70},{\"price\":8.55,\"quantity\":84825,\"orders\":62},{\"price\":8.5,\"quantity\":50245,\"orders\":44},{\"price\":8.45,\"quantity\":42250,\"orders\":32}]\nasks\n[{\"price\":8.7,\"quantity\":15665,\"orders\":13},{\"price\":8.75,\"quantity\":81835,\"orders\":66},{\"price\":8.8,\"quantity\":72215,\"orders\":58},{\"price\":8.85,\"quantity\":14950,\"orders\":16},{\"price\":8.9,\"quantity\":31980,\"orders\":28}]\noption_side\nPUT\nstrike\n23850.0\nexpiry\n2026-06-16\ntick_validity\nOK\nreject_reason\n\nis_selected_option\nFalse\nis_shadow_option\nFalse\n",
      "type": "stream"
    },
    "ticks:mme:opt:stream": {
      "len": 2169,
      "tail": "1781587557073-0\ninstrument_key\nNFO:NIFTY2661623850PE\ninstrument_role\nPE_ATM1\nts_event_ns\n1781607356000000000\nprovider_id\nZERODHA\nprovider_role\nselected_option_marketdata\nexchange\nNFO\ninstrument_token\n12956162\ntrading_symbol\nNIFTY2661623850PE\nts_provider_ns\n1781607356000000000\nts_recv_ns\n1781587557069260121\nseq_no\n\nltp\n8.7\nlast_qty\n\nvolume\n0\noi\n\nbid\n8.65\nask\n8.7\nbid_qty\n31265\nask_qty\n15665\nbids\n[{\"price\":8.65,\"quantity\":31265,\"orders\":34},{\"price\":8.6,\"quantity\":88205,\"orders\":70},{\"price\":8.55,\"quantity\":84825,\"orders\":62},{\"price\":8.5,\"quantity\":50245,\"orders\":44},{\"price\":8.45,\"quantity\":42250,\"orders\":32}]\nasks\n[{\"price\":8.7,\"quantity\":15665,\"orders\":13},{\"price\":8.75,\"quantity\":81835,\"orders\":66},{\"price\":8.8,\"quantity\":72215,\"orders\":58},{\"price\":8.85,\"quantity\":14950,\"orders\":16},{\"price\":8.9,\"quantity\":31980,\"orders\":28}]\noption_side\nPUT\nstrike\n23850.0\nexpiry\n2026-06-16\ntick_validity\nOK\nreject_reason\n\nis_selected_option\nFalse\nis_shadow_option\nFalse\n",
      "type": "stream"
    }
  },
  "base_live_visible": true,
  "classification": "REVIEW_CONTROLLED_PAPER_R1B_DANGER_STREAM_NONZERO_NO_ARM_NO_ORDER",
  "danger_env_absent": true,
  "danger_nonzero": {
    "state:execution": {
      "len": 19,
      "sample": "mode\nNORMAL\nexecution_mode\nNORMAL\nservice_state\nSTOPPING\nentry_pending\n0\nexit_pending\n0\nbroker_connected\n1\nbroker_degraded\n0\nlock_owned\n1\nlast_decision_id\nstrategy-hold-1781585153713390362\nlast_ack_type\nRECEIVED\nlast_error\n\npending_order_json\n\nactive_execution_provider_id\nZERODHA\nprimary_execution_provider_id\nZERODHA\nfallback_execution_provider_id\nUNAVAILABLE\nprovider_route_reason\nprimary_only\nprovider_failover_used\n0\nupdated_at_ns\n1781587118753389118\nts_ns\n1781587118753389118\n",
      "type": "hash"
    },
    "state:risk": {
      "len": 52,
      "sample": "ts_ns\n1781587116146411263\nts_event_ns\n1781587116146411263\ncontrol_mode\nNORMAL\nmode\nNORMAL\nveto_entries\n1\ndegraded_only\n0\nforce_flatten\n0\nallow_exits\n1\nmanual_pause\n0\nmanual_pause_reason\n\ntrading_window_ok\n1\nexecution_healthy\n1\nexecution_state_known\n1\nposition_state_known\n1\nposition_open\n0\nupstream_healthy\n1\nfeeds_heartbeat_fresh\n1\nfeatures_heartbeat_fresh\n1\nstrategy_heartbeat_fresh\n1\nexecution_heartbeat_fresh\n1\nbroker_connected\n1\ncooldown_until_ns\n0\ncooldown_active\n0\nday_realized_pnl\n0.0\ntrades_today\n0\nday_loss_count\n0\nday_win_count\n0\nconsecutive_losses\n0\ntrading_day\n2026-06-16\nstale\n0\nrisk_heartbeat_stale\n0\ndaily_stop_hit\n0\nmax_loss_hit\n0\nmax_trades_hit\n0\nmax_new_lots\n0\nparams_reload_requested\n0\nreason_code\nCONTROLLED_PAPER_NOT_ARMED\nreason_message\nCONTROLLED_PAPER_NOT_ARMED\nlast_update_ns\n1781587116146411263\nlast_trade_id\n\nlast_trade_stream_id\n0-0\nlast_trade_ts_ns\n0\nlast_pnl_source\n\nprocessed_ledger_event_keys\n\nreplay_mode\n0\nrisk_keys_trades_stream\ntrades:ledger:stream\nrisk_keys_cmd_stream\ncmd:mme:stream\nrisk_keys_state_hash\nstate:risk\nrisk_blocks_entries_only\n1\ncontrolled_paper_entry_veto\n1\ncontrolled_paper_veto_reason\nCONTROLLED_PAPER_NOT_ARMED\ncontrolled_paper_veto_detail\n\n",
      "type": "hash"
    }
  },
  "disk_file": "run/audits/LANE-X-CONTROLLED-PAPER-R1B_CLEAN_SEMANTIC_PREFLIGHT_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_105550_disk.txt",
  "fail_closed_visible": false,
  "flat_semantic": true,
  "git_status": "run/audits/LANE-X-CONTROLLED-PAPER-R1B_CLEAN_SEMANTIC_PREFLIGHT_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_105550_git_status.txt",
  "next_step": "This is audit only. Do not arm paper unless user gives explicit separate approval and gate/route is proven acceptable.",
  "no_activation_patch": true,
  "no_execution_start": true,
  "no_family_order_patch": true,
  "no_features_patch": true,
  "no_order": true,
  "no_paper_armed": true,
  "no_paper_order": true,
  "no_redis_delete": true,
  "no_registry_patch": true,
  "no_risk_start": true,
  "no_source_patch": true,
  "no_strategy_patch": true,
  "observe_env_ok": true,
  "paper_gate_visible": true,
  "paper_like_keys": {},
  "position": {
    "avg_price": "",
    "broker_order_id": "",
    "decision_id": "",
    "entry_mode": "",
    "entry_option_symbol": "",
    "entry_option_token": "",
    "entry_strike": "",
    "entry_ts_ns": "",
    "has_position": "0",
    "mark_price": "",
    "position_side": "FLAT",
    "qty_lots": "0",
    "qty_units": "0",
    "realized_pnl_day": "0"
  },
  "process_present": true,
  "redis_state": "run/audits/LANE-X-CONTROLLED-PAPER-R1B_CLEAN_SEMANTIC_PREFLIGHT_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_105550_redis_semantic_state.json",
  "route_allowed_visible": false,
  "status_file": "run/audits/LANE-X-CONTROLLED-PAPER-R1B_CLEAN_SEMANTIC_PREFLIGHT_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_105550_status.txt",
  "status_terms": {
    "mentions_fail_closed": false,
    "mentions_flat": false,
    "mentions_order_zero": true,
    "mentions_paper": true,
    "mentions_pstatus": true,
    "mentions_route_allowed_true": false,
    "paper_status_helper_found": false,
    "pstatus_helper_found": false
  },
  "tag": "LANE-X-CONTROLLED-PAPER-R1B_CLEAN_SEMANTIC_PREFLIGHT_NO_ARM_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_105550"
}
```

## Status excerpt

```text
ns=1781587553220553892
frame_valid=1
strategy_mode=AUTO
system_state=SCANNING
ts_event_ns=1781587553220553892
warmup_complete=1

[state:baselines:mme:fut]
updated_at=2026-06-16 10:55:53 age=3.34s
family_features_version=1.1
frame_ts_ns=1781587553220553892
regime=FAST

[state:option:confirm]
updated_at=2026-06-16 10:55:53 age=3.34s
frame_ts_ns=1781587553220553892

====================================================================================================
LATEST STREAM ENTRIES (feeds/features/system)
====================================================================================================

[ticks:mme:fut:stream]
id=1781587554094-0 | ts=2026-06-16 16:25:53 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23990.0 | bid=23988.1 | ask=23990.0
id=1781587552837-0 | ts=2026-06-16 16:25:52 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23990.0 | bid=23988.1 | ask=23990.0

[ticks:mme:opt:stream]
id=1781587556087-0 | ts=2026-06-16 16:25:55 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623850PE | instrument_token=12956162 | trading_symbol=NIFTY2661623850PE | instrument_role=PE_ATM1 | ltp=8.55 | bid=8.6 | ask=8.65
id=1781587555046-0 | ts=2026-06-16 16:25:54 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623850PE | instrument_token=12956162 | trading_symbol=NIFTY2661623850PE | instrument_role=PE_ATM1 | ltp=8.7 | bid=8.7 | ask=8.75

[features:mme:stream]
id=1781587553548-0 | ts=2026-06-16 10:55:53 | age=3.35s | frame_id=features-1781587553220553892
id=1781587550279-0 | ts=2026-06-16 10:55:49 | age=6.62s | frame_id=features-1781587549953997928

[system:health:stream]
id=1781587556539-0 | ts=2026-06-16 10:55:56 | age=0.04s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1
id=1781587556485-0 | ts=2026-06-16 10:55:56 | age=0.09s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | status=OK | detail=ticks_flowing | selection_version=mme-instruments-v1

[system:errors:stream]
id=1781587118263-0 | ts=2026-06-16 10:48:38 | age=438.31s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118211-0 | ts=2026-06-16 10:48:38 | age=438.36s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

[ticks:mme:fut:zerodha:stream]
id=1781587554092-0 | ts=2026-06-16 16:25:53 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23990.0 | bid=23988.1 | ask=23990.0
id=1781587552834-0 | ts=2026-06-16 16:25:52 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY26JUNFUT | instrument_token=15956226 | trading_symbol=NIFTY26JUNFUT | instrument_role=FUTURES | ltp=23990.0 | bid=23988.1 | ask=23990.0

[ticks:mme:fut:dhan:stream]
no entries

[ticks:mme:opt:selected:zerodha:stream]
id=1781587556085-0 | ts=2026-06-16 16:25:55 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623850PE | instrument_token=12956162 | trading_symbol=NIFTY2661623850PE | instrument_role=PE_ATM1 | ltp=8.55 | bid=8.6 | ask=8.65
id=1781587555044-0 | ts=2026-06-16 16:25:54 | age=0.00s | provider_id=ZERODHA | instrument_key=NFO:NIFTY2661623850PE | instrument_token=12956162 | trading_symbol=NIFTY2661623850PE | instrument_role=PE_ATM1 | ltp=8.7 | bid=8.7 | ask=8.75

[ticks:mme:opt:selected:dhan:stream]
no entries

[ticks:mme:opt:context:dhan:stream]
no entries

[provider:runtime:stream]
id=1781587556538-0 | ts=2026-06-16 10:55:56 | age=0.04s | family_runtime_mode=OBSERVE_ONLY
id=1781587556484-0 | ts=2026-06-16 10:55:56 | age=0.09s | family_runtime_mode=OBSERVE_ONLY

====================================================================================================
LAST SYSTEM ERRORS
====================================================================================================
id=1781587118263-0 | ts=2026-06-16 10:48:38 | age=438.31s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118211-0 | ts=2026-06-16 10:48:38 | age=438.37s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118157-0 | ts=2026-06-16 10:48:38 | age=438.42s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118103-0 | ts=2026-06-16 10:48:38 | age=438.47s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587118050-0 | ts=2026-06-16 10:48:38 | age=438.53s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117996-0 | ts=2026-06-16 10:48:37 | age=438.58s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117944-0 | ts=2026-06-16 10:48:37 | age=438.63s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117890-0 | ts=2026-06-16 10:48:37 | age=438.69s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117834-0 | ts=2026-06-16 10:48:37 | age=438.74s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1
id=1781587117781-0 | ts=2026-06-16 10:48:37 | age=438.80s | service_name=feeds | instance_id=feeds:mme-scalpx:60050 | error_type=feeds_service_loop_error | detail=FeedStartupError:feeds singleton lock refresh failed | selection_version=mme-instruments-v1

===== pstatus =====
pstatus_not_found

===== paper_status =====
paper_status_not_found

```

## Safety

NO source patch
NO features.py patch
NO strategy.py patch
NO registry patch
NO activation patch
NO FAMILY_ORDER patch
NO broker order
NO paper armed
NO paper order
NO risk start
NO execution start
NO Redis delete
