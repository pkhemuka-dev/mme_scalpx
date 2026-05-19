# A6-FEED-R5AM-R2_corrected_read_only_rank_actual_stage_flags_tradability_patch_surface_after_r5am_no_patch_no_restart_no_order_no_paper_20260515_151733

Batch: A6-FEED-R5AM-R2

Purpose: corrected_read_only_rank_actual_stage_flags_tradability_patch_surface_after_r5am_no_patch_no_restart_no_order_no_paper

Final verdict: FAIL_A6_FEED_R5AM_R2_SURFACE_RANKING_OR_SAFETY_CHECK

Safety: read-only patch-surface ranking only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "contract_candidate_count": 2,
  "decisions_stream_age_ms": 19466177,
  "decisions_stream_xlen": 1684,
  "dict_candidate_count": 40,
  "features_stream_age_ms": 16181870,
  "features_stream_xlen": 131,
  "likely_condition": "SURFACE_RANKING_OR_SAFETY_CHECK_FAILED",
  "next_action": "Stop and review proof.",
  "r5ak_final_verdict": "PASS_A6_FEED_R5AK_STAGE_FLAGS_CONTRACT_ALIGNMENT_PATCH_PLAN_READY_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ak_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AK_read_only_stage_flags_contract_alignment_patch_plan_no_patch_no_restart_no_order_no_paper_20260515_150204.json",
  "r5al_final_verdict": "FAIL_A6_FEED_R5AL_STAGE_FLAGS_PATCH_OR_SAFETY_CHECK",
  "r5al_patch_applied": null,
  "r5al_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AL_narrow_stage_flags_contract_alignment_patch_remove_extra_tradability_flag_no_restart_no_order_no_paper_20260515_150353.json",
  "r5am_failures": [
    "latest_r5al_failure_found"
  ],
  "r5am_final_verdict": "FAIL_A6_FEED_R5AM_SAFETY_OR_SURFACE_LOCATION_CHECK",
  "r5am_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AM_read_only_locate_actual_stage_flags_tradability_producer_and_contract_surface_after_r5al_no_patch_no_restart_no_order_no_paper_20260515_150550.json",
  "ranked_patch_surface_count": 18,
  "services": [],
  "top_ranked_patch_surfaces": [
    {
      "candidate": {
        "classification": "validator_expected_keys_likely_patch_target_add_tradability_ok",
        "file": "app/mme_scalpx/services/feature_family/contracts.py",
        "has_canonical_four": true,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": false,
        "line": 234,
        "values": [
          "data_valid",
          "data_quality_ok",
          "session_eligible",
          "warmup_complete",
          "risk_veto_active",
          "reconciliation_lock_active",
          "active_position_present",
          "provider_ready_classic",
          "provider_ready_miso",
          "dhan_context_fresh",
          "selected_option_present",
          "futures_present",
          "call_present",
          "put_present"
        ],
        "window": "    218:     \"premium_floor_ok\",\n    219: )\n    220: \n    221: COMMON_KEYS: Final[tuple[str, ...]] = (\n    222:     \"regime\",\n    223:     \"strategy_runtime_mode_classic\",\n    224:     \"strategy_runtime_mode_miso\",\n    225:     \"futures\",\n    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"risk_veto_active\",\n    240:     \"reconciliation_lock_active\",\n    241:     \"active_position_present\",\n    242:     \"provider_ready_classic\",\n    243:     \"provider_ready_miso\",\n    244:     \"dhan_context_fresh\",\n    245:     \"selected_option_present\",\n    246:     \"futures_present\",\n    247:     \"call_present\",\n    248:     \"put_present\",\n    249: )\n    250: "
      },
      "patch_direction": "add tradability_ok to stage_flags expected keys in validator contract",
      "rank": 1,
      "reason": "producers/feature-family surfaces reference tradability_ok, while validator expected set appears canonical-four only"
    },
    {
      "candidate": {
        "classification": "supporting_reference",
        "end_line": 407,
        "file": "app/mme_scalpx/services/feature_family/common.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "delta_3",
          "depth_ok",
          "depth_total",
          "lot_size",
          "ltp",
          "micro_edge",
          "microprice",
          "ofi_ratio_proxy",
          "response_efficiency",
          "spread",
          "spread_ratio",
          "strike",
          "tick_size",
          "top5_ask_qty",
          "top5_bid_qty",
          "tradability_ok"
        ],
        "line": 390,
        "score": 50,
        "window": "    374:         \"ema9_slope\": _safe_float(kwargs.get(\"ema9_slope\"), None),\n    375:         \"ema21_slope\": _safe_float(kwargs.get(\"ema21_slope\"), None),\n    376:         \"delta_3\": _safe_float(kwargs.get(\"delta_3\"), None),\n    377:         \"vel_3\": _safe_float(kwargs.get(\"vel_3\"), None),\n    378:         \"vel_ratio\": _safe_float(kwargs.get(\"vel_ratio\", kwargs.get(\"velocity_ratio\")), None),\n    379:         \"vol_delta\": _safe_float(kwargs.get(\"vol_delta\"), None),\n    380:         \"vol_norm\": _safe_float(kwargs.get(\"vol_norm\"), None),\n    381:         \"range_fast\": _safe_float(kwargs.get(\"range_fast\"), None),\n    382:         \"range_slow\": _safe_float(kwargs.get(\"range_slow\"), None),\n    383:         \"range_ratio\": _safe_float(kwargs.get(\"range_ratio\"), None),\n    384:         \"above_vwap\": _safe_bool(kwargs.get(\"above_vwap\"), False),\n    385:         \"below_vwap\": _safe_bool(kwargs.get(\"below_vwap\"), False),\n    386:     }\n    387: \n    388: \n    389: def build_common_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:\n >> 390:     return {\n    391:         \"ltp\": _safe_float(kwargs.get(\"ltp\"), None),\n    392:         \"spread\": _safe_float(kwargs.get(\"spread\"), None),\n    393:         \"spread_ratio\": _safe_float(kwargs.get(\"spread_ratio\"), None),\n    394:         \"depth_total\": _safe_int(kwargs.get(\"depth_total\"), 0) or None,\n    395:         \"depth_ok\": _safe_bool(kwargs.get(\"depth_ok\"), False),\n    396:         \"top5_bid_qty\": _safe_int(kwargs.get(\"top5_bid_qty\", kwargs.get(\"bid_qty_5\")), 0) or None,\n    397:         \"top5_ask_qty\": _safe_int(kwargs.get(\"top5_ask_qty\", kwargs.get(\"ask_qty_5\")), 0) or None,\n    398:         \"ofi_ratio_proxy\": _safe_float(kwargs.get(\"ofi_ratio_proxy\", kwargs.get(\"weighted_ofi_persist\")), None),\n    399:         \"microprice\": _safe_float(kwargs.get(\"microprice\"), None),\n    400:         \"micro_edge\": _safe_float(kwargs.get(\"micro_edge\"), None),\n    401:         \"delta_3\": _safe_float(kwargs.get(\"delta_3\"), None),\n    402:         \"response_efficiency\": _safe_float(kwargs.get(\"response_efficiency\"), None),\n    403:         \"tradability_ok\": _safe_bool(kwargs.get(\"tradability_ok\"), False),\n    404:         \"tick_size\": _safe_float(kwargs.get(\"tick_size\"), None),\n    405:         \"lot_size\": _safe_int(kwargs.get(\"lot_size\"), 0) or None,\n    406:         \"strike\": _safe_float(kwargs.get(\"strike\"), None),"
      },
      "patch_direction": "supporting reference only",
      "rank": 2,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    },
    {
      "candidate": {
        "classification": "supporting_reference",
        "end_line": 425,
        "file": "app/mme_scalpx/services/feature_family/common.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "delta_3",
          "depth_ok",
          "depth_total",
          "ltp",
          "micro_edge",
          "microprice",
          "ofi_ratio_proxy",
          "response_efficiency",
          "side",
          "spread",
          "spread_ratio",
          "tradability_ok"
        ],
        "line": 412,
        "score": 50,
        "window": "    396:         \"top5_bid_qty\": _safe_int(kwargs.get(\"top5_bid_qty\", kwargs.get(\"bid_qty_5\")), 0) or None,\n    397:         \"top5_ask_qty\": _safe_int(kwargs.get(\"top5_ask_qty\", kwargs.get(\"ask_qty_5\")), 0) or None,\n    398:         \"ofi_ratio_proxy\": _safe_float(kwargs.get(\"ofi_ratio_proxy\", kwargs.get(\"weighted_ofi_persist\")), None),\n    399:         \"microprice\": _safe_float(kwargs.get(\"microprice\"), None),\n    400:         \"micro_edge\": _safe_float(kwargs.get(\"micro_edge\"), None),\n    401:         \"delta_3\": _safe_float(kwargs.get(\"delta_3\"), None),\n    402:         \"response_efficiency\": _safe_float(kwargs.get(\"response_efficiency\"), None),\n    403:         \"tradability_ok\": _safe_bool(kwargs.get(\"tradability_ok\"), False),\n    404:         \"tick_size\": _safe_float(kwargs.get(\"tick_size\"), None),\n    405:         \"lot_size\": _safe_int(kwargs.get(\"lot_size\"), 0) or None,\n    406:         \"strike\": _safe_float(kwargs.get(\"strike\"), None),\n    407:     }\n    408: \n    409: \n    410: def build_selected_option_block(*, side: str | None = None, **kwargs: Any) -> dict[str, Any]:\n    411:     base = build_common_option_block(side=side, **kwargs)\n >> 412:     return {\n    413:         \"side\": _safe_str(side or kwargs.get(\"side\")) or None,\n    414:         \"ltp\": base[\"ltp\"],\n    415:         \"spread\": base[\"spread\"],\n    416:         \"spread_ratio\": base[\"spread_ratio\"],\n    417:         \"depth_total\": base[\"depth_total\"],\n    418:         \"depth_ok\": base[\"depth_ok\"],\n    419:         \"ofi_ratio_proxy\": base[\"ofi_ratio_proxy\"],\n    420:         \"microprice\": base[\"microprice\"],\n    421:         \"micro_edge\": base[\"micro_edge\"],\n    422:         \"delta_3\": base[\"delta_3\"],\n    423:         \"response_efficiency\": base[\"response_efficiency\"],\n    424:         \"tradability_ok\": base[\"tradability_ok\"],\n    425:     }\n    426: \n    427: \n    428: def build_cross_option_block("
      },
      "patch_direction": "supporting reference only",
      "rank": 3,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    },
    {
      "candidate": {
        "classification": "supporting_reference",
        "end_line": 808,
        "file": "app/mme_scalpx/services/feature_family/contracts.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "delta_3",
          "depth_ok",
          "depth_total",
          "lot_size",
          "ltp",
          "micro_edge",
          "microprice",
          "ofi_ratio_proxy",
          "response_efficiency",
          "spread",
          "spread_ratio",
          "strike",
          "tick_size",
          "top5_ask_qty",
          "top5_bid_qty",
          "tradability_ok"
        ],
        "line": 791,
        "score": 50,
        "window": "    775:         \"ema9_slope\": None,\n    776:         \"ema21_slope\": None,\n    777:         \"delta_3\": None,\n    778:         \"vel_3\": None,\n    779:         \"vel_ratio\": None,\n    780:         \"vol_delta\": None,\n    781:         \"vol_norm\": None,\n    782:         \"range_fast\": None,\n    783:         \"range_slow\": None,\n    784:         \"range_ratio\": None,\n    785:         \"above_vwap\": None,\n    786:         \"below_vwap\": None,\n    787:     }\n    788: \n    789: \n    790: def build_empty_common_option_block() -> dict[str, Any]:\n >> 791:     return {\n    792:         \"ltp\": None,\n    793:         \"spread\": None,\n    794:         \"spread_ratio\": None,\n    795:         \"depth_total\": None,\n    796:         \"depth_ok\": False,\n    797:         \"top5_bid_qty\": None,\n    798:         \"top5_ask_qty\": None,\n    799:         \"ofi_ratio_proxy\": None,\n    800:         \"microprice\": None,\n    801:         \"micro_edge\": None,\n    802:         \"delta_3\": None,\n    803:         \"response_efficiency\": None,\n    804:         \"tradability_ok\": False,\n    805:         \"tick_size\": None,\n    806:         \"lot_size\": None,\n    807:         \"strike\": None,"
      },
      "patch_direction": "supporting reference only",
      "rank": 4,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    },
    {
      "candidate": {
        "classification": "supporting_reference",
        "end_line": 825,
        "file": "app/mme_scalpx/services/feature_family/contracts.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "delta_3",
          "depth_ok",
          "depth_total",
          "ltp",
          "micro_edge",
          "microprice",
          "ofi_ratio_proxy",
          "response_efficiency",
          "side",
          "spread",
          "spread_ratio",
          "tradability_ok"
        ],
        "line": 812,
        "score": 50,
        "window": "    796:         \"depth_ok\": False,\n    797:         \"top5_bid_qty\": None,\n    798:         \"top5_ask_qty\": None,\n    799:         \"ofi_ratio_proxy\": None,\n    800:         \"microprice\": None,\n    801:         \"micro_edge\": None,\n    802:         \"delta_3\": None,\n    803:         \"response_efficiency\": None,\n    804:         \"tradability_ok\": False,\n    805:         \"tick_size\": None,\n    806:         \"lot_size\": None,\n    807:         \"strike\": None,\n    808:     }\n    809: \n    810: \n    811: def build_empty_selected_option_block() -> dict[str, Any]:\n >> 812:     return {\n    813:         \"side\": None,\n    814:         \"ltp\": None,\n    815:         \"spread\": None,\n    816:         \"spread_ratio\": None,\n    817:         \"depth_total\": None,\n    818:         \"depth_ok\": False,\n    819:         \"ofi_ratio_proxy\": None,\n    820:         \"microprice\": None,\n    821:         \"micro_edge\": None,\n    822:         \"delta_3\": None,\n    823:         \"response_efficiency\": None,\n    824:         \"tradability_ok\": False,\n    825:     }\n    826: \n    827: \n    828: def build_empty_cross_option_block() -> dict[str, Any]:"
      },
      "patch_direction": "supporting reference only",
      "rank": 5,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    },
    {
      "candidate": {
        "classification": "supporting_reference",
        "end_line": 733,
        "file": "app/mme_scalpx/services/feature_family/option_core.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "depth_ok",
          "depth_total_min",
          "premium_floor_min",
          "premium_floor_ok",
          "response_efficiency_min",
          "response_efficiency_ok",
          "spread_ratio_max",
          "spread_ratio_ok",
          "tradability_ok"
        ],
        "line": 718,
        "score": 50,
        "window": "    702:     response_eff_value = _safe_float(response_efficiency, None)\n    703: \n    704:     premium_floor_ok = bool(\n    705:         premium is not None and premium >= max(float(premium_floor_min), 0.0)\n    706:     )\n    707:     depth_ok = bool(\n    708:         depth_total_value is not None and depth_total_value >= max(int(depth_total_min), 0)\n    709:     )\n    710:     spread_ratio_ok = bool(\n    711:         spread_ratio_value is not None and spread_ratio_value <= max(float(spread_ratio_max), 0.0)\n    712:     )\n    713:     response_efficiency_ok = bool(\n    714:         response_eff_value is not None\n    715:         and response_eff_value >= float(response_efficiency_min)\n    716:     )\n    717: \n >> 718:     return {\n    719:         \"premium_floor_min\": float(premium_floor_min),\n    720:         \"depth_total_min\": int(depth_total_min),\n    721:         \"spread_ratio_max\": float(spread_ratio_max),\n    722:         \"response_efficiency_min\": float(response_efficiency_min),\n    723:         \"premium_floor_ok\": premium_floor_ok,\n    724:         \"depth_ok\": depth_ok,\n    725:         \"spread_ratio_ok\": spread_ratio_ok,\n    726:         \"response_efficiency_ok\": response_efficiency_ok,\n    727:         \"tradability_ok\": bool(\n    728:             premium_floor_ok\n    729:             and depth_ok\n    730:             and spread_ratio_ok\n    731:             and response_efficiency_ok\n    732:         ),\n    733:     }\n    734: "
      },
      "patch_direction": "supporting reference only",
      "rank": 6,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    },
    {
      "candidate": {
        "classification": "features_or_projection_surface_mentions_tradability",
        "end_line": 5650,
        "file": "app/mme_scalpx/services/features.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "ask",
          "ask_qty",
          "ask_qty_5",
          "best_ask",
          "best_bid",
          "bid",
          "bid_qty",
          "bid_qty_5",
          "delta",
          "depth_total",
          "instrument_key",
          "instrument_token",
          "iv",
          "ltp",
          "oi",
          "oi_change",
          "option_side",
          "option_symbol",
          "option_token",
          "present",
          "provider_id",
          "raw",
          "role",
          "side",
          "source_member_key",
          "spread",
          "spread_ratio",
          "strike",
          "tradability_ok",
          "trading_symbol",
          "ts_event_ns",
          "valid",
          "volume"
        ],
        "line": 5616,
        "score": 50,
        "window": "    5600:     )\n    5601:     if isinstance(built, Mapping):\n    5602:         return built\n    5603: \n    5604:     bid = _feed_best_price(surface, \"bid\")\n    5605:     ask = _feed_best_price(surface, \"ask\")\n    5606:     bid_qty_5 = _feed_depth_qty(surface, \"bid\")\n    5607:     ask_qty_5 = _feed_depth_qty(surface, \"ask\")\n    5608:     ltp = _feed_ltp(surface)\n    5609:     depth_total = bid_qty_5 + ask_qty_5\n    5610:     spread = max(0.0, ask - bid) if ask > 0.0 and bid > 0.0 else 0.0\n    5611:     strike = _safe_float_or_none(_pick(surface, \"strike\", \"strike_price\", \"strikePrice\"))\n    5612: \n    5613:     present = bool(ltp > 0.0 or bid > 0.0 or ask > 0.0 or depth_total > 0.0)\n    5614:     valid = bool(present and resolved_side in {\"CALL\", \"PUT\"} and strike is not None)\n    5615: \n >> 5616:     return {\n    5617:         \"present\": present,\n    5618:         \"valid\": valid,\n    5619:         \"side\": resolved_side,\n    5620:         \"option_side\": resolved_side,\n    5621:         \"role\": role or _safe_str(_pick(surface, \"role\"), \"SELECTED_OPTION\"),\n    5622:         \"provider_id\": resolved_provider_id,\n    5623:         \"instrument_key\": _feed_instrument_key(surface),\n    5624:         \"instrument_token\": _feed_token(surface),\n    5625:         \"option_token\": _feed_token(surface),\n    5626:         \"trading_symbol\": _feed_trading_symbol(surface),\n    5627:         \"option_symbol\": _feed_trading_symbol(surface),\n    5628:         \"strike\": strike,\n    5629:         \"ltp\": ltp,\n    5630:         \"best_bid\": bid,\n    5631:         \"best_ask\": ask,\n    5632:         \"bid\": bid,"
      },
      "patch_direction": "supporting reference only",
      "rank": 7,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    },
    {
      "candidate": {
        "classification": "features_or_projection_surface_mentions_tradability",
        "end_line": 6922,
        "file": "app/mme_scalpx/services/features.py",
        "has_canonical_four": false,
        "has_canonical_plus_tradability": false,
        "has_tradability_ok": true,
        "keys": [
          "anomaly",
          "best_ask",
          "best_bid",
          "book_ok",
          "depth_ok",
          "depth_total",
          "ltp",
          "quote_ok",
          "selected_present",
          "side",
          "spread",
          "spread_ok",
          "spread_ratio",
          "tradability_ok"
        ],
        "line": 6907,
        "score": 50,
        "window": "    6891:     side = str(selected.get(\"side\") or selected.get(\"option_side\") or \"\").upper()\n    6892:     ltp = _batch26o16h_r2_float(selected.get(\"ltp\") or selected.get(\"last_price\"), 0.0)\n    6893:     spread_ratio = _batch26o16h_r2_float(selected.get(\"spread_ratio\"), 0.0)\n    6894:     spread = _batch26o16h_r2_float(selected.get(\"spread\"), 0.0)\n    6895:     depth_total = int(_batch26o16h_r2_float(selected.get(\"depth_total\"), 0.0))\n    6896:     best_bid = _batch26o16h_r2_float(selected.get(\"best_bid\"), 0.0)\n    6897:     best_ask = _batch26o16h_r2_float(selected.get(\"best_ask\"), 0.0)\n    6898:     anomaly = bool(selected.get(\"anomaly_clamped\")) or str(selected.get(\"tick_validity\") or \"\").upper() == \"ANOMALY_CLAMPED\"\n    6899: \n    6900:     selected_present = bool(side in {\"CALL\", \"PUT\"} and ltp > 0.0)\n    6901:     spread_ok = bool(spread >= 0.0 and (spread_ratio == 0.0 or spread_ratio <= 0.03))\n    6902:     depth_ok = bool(depth_total > 0 or selected.get(\"depth_ok\") is True)\n    6903:     quote_ok = bool(ltp > 0.0 and spread_ok)\n    6904:     book_ok = bool(depth_ok and (best_bid >= 0.0) and (best_ask >= 0.0))\n    6905:     tradability_ok = bool(selected_present and quote_ok and depth_ok and book_ok and not anomaly)\n    6906: \n >> 6907:     return {\n    6908:         \"side\": side,\n    6909:         \"ltp\": ltp,\n    6910:         \"spread\": spread,\n    6911:         \"spread_ratio\": spread_ratio,\n    6912:         \"depth_total\": depth_total,\n    6913:         \"best_bid\": best_bid,\n    6914:         \"best_ask\": best_ask,\n    6915:         \"anomaly\": anomaly,\n    6916:         \"selected_present\": selected_present,\n    6917:         \"spread_ok\": spread_ok,\n    6918:         \"depth_ok\": depth_ok,\n    6919:         \"quote_ok\": quote_ok,\n    6920:         \"book_ok\": book_ok,\n    6921:         \"tradability_ok\": tradability_ok,\n    6922:     }\n    6923: "
      },
      "patch_direction": "supporting reference only",
      "rank": 8,
      "reason": "contains tradability_ok but not the primary validator expected-key surface"
    }
  ]
}
```

Required checks:

```json
{
  "all_searched_sources_compile": true,
  "all_watched_sources_compile": true,
  "dict_candidates_or_contract_candidates_found": true,
  "latest_r5ak_plan_ready_found": true,
  "latest_r5al_found_and_no_patch_applied": false,
  "latest_r5am_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "r5am_surface_output_available_even_if_failed": [
    {
      "end_lineno": 407,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 390
    },
    {
      "end_lineno": 425,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 412
    },
    {
      "end_lineno": 548,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": true,
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "data_quality_ok",
        "data_valid",
        "dhan_context_fresh",
        "futures_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "put_present",
        "reconciliation_lock_active",
        "risk_veto_active",
        "selected_option_present",
        "session_eligible",
        "warmup_complete"
      ],
      "lineno": 533
    },
    {
      "end_lineno": 781,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "common",
        "families",
        "family_features_version",
        "generated_at_ns",
        "market",
        "provider_runtime",
        "schema_version",
        "service",
        "snapshot",
        "stage_flags"
      ],
      "lineno": 767
    },
    {
      "end_lineno": 808,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 791
    },
    {
      "end_lineno": 825,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 812
    },
    {
      "end_lineno": 888,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": true,
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "data_quality_ok",
        "data_valid",
        "dhan_context_fresh",
        "futures_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "put_present",
        "reconciliation_lock_active",
        "risk_veto_active",
        "selected_option_present",
        "session_eligible",
        "warmup_complete"
      ],
      "lineno": 873
    },
    {
      "end_lineno": 1056,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "common",
        "families",
        "family_features_version",
        "generated_at_ns",
        "market",
        "provider_runtime",
        "schema_version",
        "service",
        "snapshot",
        "stage_flags"
      ],
      "lineno": 1045
    },
    {
      "end_lineno": 733,
      "file": "app/mme_scalpx/services/feature_family/option_core.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "depth_total_min",
        "premium_floor_min",
        "premium_floor_ok",
        "response_efficiency_min",
        "response_efficiency_ok",
        "spread_ratio_max",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 718
    },
    {
      "end_lineno": 3930,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "action",
        "branch_frames",
        "common",
        "data_valid",
        "family_frames",
        "family_status",
        "family_surfaces",
        "features_generated_at_ns",
        "frame_id",
        "frame_ts_ns",
        "hold_only",
        "mapping_repair",
        "market",
        "provider_ready_classic",
        "provider_ready_miso",
        "provider_runtime",
        "reason",
        "regime",
        "safe_to_consume",
        "stage_flags",
        "view_version",
        "warmup_complete"
      ],
      "lineno": 3898
    },
    {
      "end_lineno": 5650,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "ask",
        "ask_qty",
        "ask_qty_5",
        "best_ask",
        "best_bid",
        "bid",
        "bid_qty",
        "bid_qty_5",
        "delta",
        "depth_total",
        "instrument_key",
        "instrument_token",
        "iv",
        "ltp",
        "oi",
        "oi_change",
        "option_side",
        "option_symbol",
        "option_token",
        "present",
        "provider_id",
        "raw",
        "role",
        "side",
        "source_member_key",
        "spread",
        "spread_ratio",
        "strike",
        "tradability_ok",
        "trading_symbol",
        "ts_event_ns",
        "valid",
        "volume"
      ],
      "lineno": 5616
    },
    {
      "end_lineno": 6922,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "anomaly",
        "best_ask",
        "best_bid",
        "book_ok",
        "depth_ok",
        "depth_total",
        "ltp",
        "quote_ok",
        "selected_present",
        "side",
        "spread",
        "spread_ok",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 6907
    },
    {
      "end_lineno": 7139,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7126
    },
    {
      "end_lineno": 7310,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7297
    },
    {
      "end_lineno": 7507,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7494
    },
    {
      "end_lineno": 1191,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "explain",
        "family_features",
        "family_frames",
        "family_surfaces",
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "generated_at_ns",
        "provider_runtime",
        "schema_version",
        "service",
        "shared_core",
        "ts_event_ns",
        "warmup_complete"
      ],
      "lineno": 1168
    },
    {
      "end_lineno": 1727,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "ask",
        "bid",
        "delta_3",
        "depth_ok",
        "depth_total",
        "instrument_key",
        "instrument_token",
        "ltp",
        "oi",
        "option_side",
        "present",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "tradability_ok",
        "trading_symbol",
        "valid",
        "volume"
      ],
      "lineno": 1705
    },
    {
      "end_lineno": 2476,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "blocked_reason",
        "depth_ok",
        "depth_total",
        "entry_pass",
        "premium_floor_ok",
        "response_efficiency",
        "response_efficiency_ok",
        "side",
        "spread_ratio",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 2464
    },
    {
      "end_lineno": 3999,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "regime",
        "selected_option",
        "warmup_complete"
      ],
      "lineno": 3992
    },
    {
      "end_lineno": 4020,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "consumer_view_json",
        "family_features_json",
        "family_features_version",
        "family_frames_json",
        "family_surfaces_json",
        "feature_state_json",
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "o20r3d_r2_validity_semantics_json",
        "o20r3d_r2a_structural_valid_json",
        "payload_json",
        "strategy_mode",
        "system_state",
        "ts_event_ns",
        "warmup_complete"
      ],
      "lineno": 4001
    },
    {
      "end_lineno": 7207,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "regime",
        "selected_option",
        "selected_option_rich",
        "warmup_complete"
      ],
      "lineno": 7199
    },
    {
      "end_lineno": 7232,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "consumer_view_json",
        "family_features_json",
        "family_features_version",
        "family_frames_json",
        "family_surfaces_json",
        "feature_state_json",
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "o17a_common_abi_json",
        "payload_json",
        "strategy_mode",
        "system_state",
        "ts_event_ns",
        "warmup_complete"
      ],
      "lineno": 7209
    },
    {
      "end_lineno": 7396,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "regime",
        "selected_option",
        "warmup_complete"
      ],
      "lineno": 7389
    },
    {
      "end_lineno": 7426,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "consumer_view_json",
        "family_features_json",
        "family_features_version",
        "family_frames_json",
        "family_surfaces_json",
        "feature_state_json",
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "o17b_common_abi_json",
        "payload_json",
        "selected_option_rich_json",
        "strategy_mode",
        "system_state",
        "ts_event_ns",
        "warmup_complete"
      ],
      "lineno": 7398
    },
    {
      "end_lineno": 2902,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "common",
        "families",
        "family_features_version",
        "generated_at_ns",
        "market",
        "provider_runtime",
        "schema_version",
        "service",
        "snapshot",
        "stage_flags"
      ],
      "lineno": 2887
    },
    {
      "end_lineno": 3242,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "nof_slope",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "spread_ticks",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok",
        "weighted_ofi_persist"
      ],
      "lineno": 3219
    },
    {
      "end_lineno": 3376,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": true,
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "cross_option_context_ready",
        "data_quality_ok",
        "data_valid",
        "dhan_context_fresh",
        "futures_present",
        "oi_wall_context_ready",
        "provider_ready",
        "provider_ready_classic",
        "provider_ready_miso",
        "put_present",
        "reconciliation_lock_active",
        "regime_ready",
        "risk_veto_active",
        "selected_option_present",
        "session_eligible",
        "warmup_complete"
      ],
      "lineno": 3323
    },
    {
      "end_lineno": 6765,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "regime",
        "selected_option",
        "warmup_complete"
      ],
      "lineno": 6758
    },
    {
      "end_lineno": 6795,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "consumer_view_json",
        "family_features_json",
        "family_features_version",
        "family_frames_json",
        "family_surfaces_json",
        "feature_state_json",
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "o16g_r2_quality_json",
        "payload_json",
        "strategy_mode",
        "system_state",
        "ts_event_ns",
        "warmup_complete"
      ],
      "lineno": 6767
    },
    {
      "end_lineno": 7046,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "regime",
        "selected_option",
        "warmup_complete"
      ],
      "lineno": 7039
    },
    {
      "end_lineno": 7074,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "consumer_view_json",
        "family_features_json",
        "family_features_version",
        "family_frames_json",
        "family_surfaces_json",
        "feature_state_json",
        "frame_id",
        "frame_ts_ns",
        "frame_valid",
        "o16h_r2_composition_json",
        "payload_json",
        "strategy_mode",
        "system_state",
        "ts_event_ns",
        "warmup_complete"
      ],
      "lineno": 7048
    },
    {
      "end_lineno": 3724,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "active_futures_provider_id",
        "active_option_context_provider_id",
        "active_selected_option_provider_id",
        "branch_id",
        "eligible",
        "family_id",
        "family_runtime_mode",
        "frame_id",
        "frame_ts_ns",
        "instrument_key",
        "instrument_token",
        "option_price",
        "option_symbol",
        "runtime_mode",
        "side",
        "stop_points",
        "strike",
        "surface",
        "target_points",
        "tick_size",
        "tradability_ok"
      ],
      "lineno": 3698
    },
    {
      "end_lineno": 6732,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "entry_pass",
        "source_bridge",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 6726
    },
    {
      "end_lineno": 7016,
      "file": "app/mme_scalpx/services/features.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "entry_pass",
        "quote_ok",
        "source_bridge",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 7009
    },
    {
      "end_lineno": 1390,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "data_valid",
        "raw",
        "safe_to_consume",
        "structural_valid"
      ],
      "lineno": 1381
    },
    {
      "end_lineno": 467,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "branch_id",
        "eligible",
        "family_id",
        "instrument_key",
        "instrument_token",
        "key",
        "option_price",
        "option_symbol",
        "side",
        "strike",
        "tradability_ok"
      ],
      "lineno": 455
    },
    {
      "end_lineno": 519,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "action",
        "branch_frames",
        "common",
        "data_valid",
        "family_frames",
        "family_status",
        "family_surfaces",
        "features_generated_at_ns",
        "frame_id",
        "frame_ts_ns",
        "hold_only",
        "market",
        "provider_ready_classic",
        "provider_ready_miso",
        "provider_runtime",
        "reason",
        "regime",
        "safe_to_consume",
        "stage_flags",
        "view_version",
        "warmup_complete"
      ],
      "lineno": 495
    },
    {
      "end_lineno": 875,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "action",
        "activation_action",
        "activation_bridge_enabled",
        "activation_candidate_count",
        "activation_mode",
        "activation_observed_action",
        "activation_promoted",
        "activation_reason",
        "activation_report_json",
        "activation_report_only",
        "activation_safe_to_promote",
        "activation_selected_action",
        "activation_selected_branch_id",
        "activation_selected_family_id",
        "activation_selected_score",
        "branch_id",
        "confidence",
        "consumer_view_json",
        "data_valid",
        "decision_id",
        "diagnostics_json",
        "doctrine_id",
        "features_generated_at_ns",
        "hold_only",
        "instrument_key",
        "instrument_token",
        "option_symbol",
        "order_type",
        "price",
        "provider_ready_classic",
        "provider_ready_miso",
        "qty",
        "reason",
        "regime",
        "safe_to_consume",
        "schema_version",
        "service",
        "side",
        "strategy_family_id",
        "strike",
        "ts_event_ns",
        "ts_ns",
        "warmup_complete"
      ],
      "lineno": 811
    },
    {
      "end_lineno": 1389,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "data_valid",
        "safe_to_consume",
        "structural_valid"
      ],
      "lineno": 1385
    },
    {
      "end_lineno": 1526,
      "file": "app/mme_scalpx/services/strategy.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "consumer_view_repair_reason",
        "consumer_view_repaired",
        "data_valid",
        "safe_to_consume",
        "structural_valid"
      ],
      "lineno": 1520
    },
    {
      "end_lineno": 407,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 390
    },
    {
      "end_lineno": 425,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 412
    },
    {
      "end_lineno": 548,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": true,
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "data_quality_ok",
        "data_valid",
        "dhan_context_fresh",
        "futures_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "put_present",
        "reconciliation_lock_active",
        "risk_veto_active",
        "selected_option_present",
        "session_eligible",
        "warmup_complete"
      ],
      "lineno": 533
    },
    {
      "end_lineno": 781,
      "file": "app/mme_scalpx/services/feature_family/common.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "common",
        "families",
        "family_features_version",
        "generated_at_ns",
        "market",
        "provider_runtime",
        "schema_version",
        "service",
        "snapshot",
        "stage_flags"
      ],
      "lineno": 767
    },
    {
      "end_lineno": 808,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "lot_size",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "spread",
        "spread_ratio",
        "strike",
        "tick_size",
        "top5_ask_qty",
        "top5_bid_qty",
        "tradability_ok"
      ],
      "lineno": 791
    },
    {
      "end_lineno": 825,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "delta_3",
        "depth_ok",
        "depth_total",
        "ltp",
        "micro_edge",
        "microprice",
        "ofi_ratio_proxy",
        "response_efficiency",
        "side",
        "spread",
        "spread_ratio",
        "tradability_ok"
      ],
      "lineno": 812
    },
    {
      "end_lineno": 888,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": true,
      "has_tradability_ok": false,
      "keys": [
        "active_position_present",
        "call_present",
        "data_quality_ok",
        "data_valid",
        "dhan_context_fresh",
        "futures_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "put_present",
        "reconciliation_lock_active",
        "risk_veto_active",
        "selected_option_present",
        "session_eligible",
        "warmup_complete"
      ],
      "lineno": 873
    },
    {
      "end_lineno": 1056,
      "file": "app/mme_scalpx/services/feature_family/contracts.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": false,
      "keys": [
        "common",
        "families",
        "family_features_version",
        "generated_at_ns",
        "market",
        "provider_runtime",
        "schema_version",
        "service",
        "snapshot",
        "stage_flags"
      ],
      "lineno": 1045
    },
    {
      "end_lineno": 733,
      "file": "app/mme_scalpx/services/feature_family/option_core.py",
      "has_canonical_stage_flags": false,
      "has_tradability_ok": true,
      "keys": [
        "depth_ok",
        "depth_total_min",
        "premium_floor_min",
        "premium_floor_ok",
        "response_efficiency_min",
        "response_efficiency_ok",
        "spread_ratio_max",
        "spread_ratio_ok",
        "tradability_ok"
      ],
      "lineno": 718
    }
  ],
  "ranked_patch_surface_found": true,
  "searched_sources_unchanged_by_this_batch": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[
  "latest_r5al_found_and_no_patch_applied"
]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AM-R2_corrected_read_only_rank_actual_stage_flags_tradability_patch_surface_after_r5am_no_patch_no_restart_no_order_no_paper_20260515_151733.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AM-R2_corrected_read_only_rank_actual_stage_flags_tradability_patch_surface_after_r5am_no_patch_no_restart_no_order_no_paper_20260515_151733_ranked_stage_flags_patch_surface_note.md
