# B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420

Classification: `PASS_R39WC_FEATURES_MISSING_DYNAMIC_SCORE_ALIAS_PUBLISHER_PATCH_PLAN_READY_NO_PATCH`

## Diagnosis
Family leaves consume dynamic score inputs, but features.py does not publish the exact score alias keys. Existing lower-level features are present in family futures surfaces but scores remain flat.

## Missing publish terms
- features_has_literal_futures_impulse_score: False
- features_has_literal_breakout_score: False
- features_has_literal_pullback_resume_score: False

## Patch target
- `app/mme_scalpx/services/features.py`

## Patch principle
Only publish aliases derived from existing surface keys. Do not lower thresholds or change family doctrine. If source fields are absent, publish explicit diagnostic fields and leave score conservative.

## Required additive fields
- surface.futures_impulse_score
- surface.breakout_score
- surface.pullback_resume_score
- surface.option_confirmation_score if already derivable
- common/feature_state selected_option delta_3 response_efficiency ofi_ratio_proxy microprice if derivable from raw samples
- payload snapshot selected_option_snapshot_ns from selected option raw ts_event_ns/ts_provider_ns when present

## Do not patch
- strategy thresholds
- candidate forcing
- safe_to_consume forcing
- paper/live/order flags
- Dhan/MISO weakening

## Current family surface map
```json
{
  "misb_call": {
    "branch_id": "CALL",
    "candidate_source_keys_available": {
      "cvd_delta": 0.0,
      "delta_3": 0.0,
      "direction_score": 0.0,
      "event_rate_spike_ratio": 0.0,
      "trend_score": 0.0,
      "velocity_ratio": 0.0,
      "volume_norm": 0.0,
      "vwap_alignment_call": true,
      "vwap_alignment_put": true,
      "weighted_ofi": 0.0,
      "weighted_ofi_persist": 0.0
    },
    "eligible": false,
    "family_id": "MISB",
    "futures_features_keys": [
      "age_ms",
      "ask",
      "ask_qty",
      "ask_qty_5",
      "bearish_flow_ok",
      "best_ask",
      "best_bid",
      "bid",
      "bid_qty",
      "bid_qty_5",
      "book_present",
      "book_pressure",
      "bullish_flow_ok",
      "context_score",
      "contradiction_score_call",
      "contradiction_score_put",
      "cvd_delta",
      "delta_3",
      "depth_total",
      "direction_label",
      "direction_score",
      "ema21_slope",
      "ema9_slope",
      "event_rate_spike_ratio",
      "fresh",
      "instrument_key",
      "instrument_token",
      "liquidity_ok",
      "live_present",
      "ltp",
      "metadata_present",
      "mid_price",
      "nof_slope",
      "present",
      "provider_id",
      "quote_present",
      "raw",
      "role",
      "role_label",
      "runtime_mode",
      "source_label",
      "source_member_key",
      "spread",
      "spread_ratio",
      "stale",
      "timestamp_present",
      "touch_depth",
      "trading_symbol",
      "trend_score",
      "ts_event_ns",
      "ts_local_ns",
      "valid",
      "velocity_ratio",
      "volume",
      "volume_norm",
      "vwap_alignment_call",
      "vwap_alignment_put",
      "vwap_distance",
      "vwap_distance_ratio",
      "weighted_ofi",
      "weighted_ofi_persist"
    ],
    "has_breakout_score": false,
    "has_futures_impulse_score": false,
    "has_pullback_resume_score": false,
    "surface_top_keys": [
      "branch_id",
      "branch_ready",
      "breakout_acceptance",
      "breakout_accepted",
      "breakout_buffer_ok",
      "breakout_extension",
      "breakout_not_overextended",
      "breakout_ref",
      "breakout_shelf_high",
      "breakout_shelf_low",
      "breakout_shelf_mid",
      "breakout_shelf_missing_reason",
      "breakout_shelf_snapshot_count",
      "breakout_shelf_valid",
      "breakout_shelf_width",
      "breakout_shelf_width_pct",
      "breakout_trigger",
      "breakout_triggered",
      "context_features",
      "context_pass",
      "continuation_support",
      "cross_option_context",
      "doctrine_id",
      "eligible",
      "entry_mode_hint",
      "failed_stage",
      "fallback_features",
      "fallback_ready",
      "family_id",
      "feature_refs",
      "futures_bias_ok",
      "futures_features",
      "near_same_side_wall",
      "oi_bias_alignment",
      "oi_wall_context",
      "option_features",
      "option_tradability_pass",
      "passed_stages",
      "premium_health",
      "present",
      "primary_features",
      "provider_ready",
      "regime",
      "regime_surface",
      "rich_surface",
      "runtime_mode",
      "runtime_mode_surface",
      "same_side_wall_strength_score",
      "selected_features",
      "setup_score",
      "shelf_confirmed",
      "shelf_valid",
      "shelf_width",
      "side",
      "strike_surface",
      "surface_kind",
      "tradability",
      "tradability_surface",
      "trend_score",
      "trend_score_ok"
    ],
    "tradability_ok": false
  },
  "misb_put": {
    "branch_id": "PUT",
    "candidate_source_keys_available": {
      "cvd_delta": 0.0,
      "delta_3": 0.0,
      "direction_score": 0.0,
      "event_rate_spike_ratio": 0.0,
      "trend_score": 0.0,
      "velocity_ratio": 0.0,
      "volume_norm": 0.0,
      "vwap_alignment_call": true,
      "vwap_alignment_put": true,
      "weighted_ofi": 0.0,
      "weighted_ofi_persist": 0.0
    },
    "eligible": false,
    "family_id": "MISB",
    "futures_features_keys": [
      "age_ms",
      "ask",
      "ask_qty",
      "ask_qty_5",
      "bearish_flow_ok",
      "best_ask",
      "best_bid",
      "bid",
      "bid_qty",
      "bid_qty_5",
      "book_present",
      "book_pressure",
      "bullish_flow_ok",
      "context_score",
      "contradiction_score_call",
      "contradiction_score_put",
      "cvd_delta",
      "delta_3",
      "depth_total",
      "direction_label",
      "direction_score",
      "ema21_slope",
      "ema9_slope",
      "event_rate_spike_ratio",
      "fresh",
      "instrument_key",
      "instrument_token",
      "liquidity_ok",
      "live_present",
      "ltp",
      "metadata_present",
      "mid_price",
      "nof_slope",
      "present",
      "provider_id",
      "quote_present",
      "raw",
      "role",
      "role_label",
      "runtime_mode",
      "source_label",
      "source_member_key",
      "spread",
      "spread_ratio",
      "stale",
      "timestamp_present",
      "touch_depth",
      "trading_symbol",
      "trend_score",
      "ts_event_ns",
      "ts_local_ns",
      "valid",
      "velocity_ratio",
      "volume",
      "volume_norm",
      "vwap_alignment_call",
      "vwap_alignment_put",
      "vwap_distance",
      "vwap_distance_ratio",
      "weighted_ofi",
      "weighted_ofi_persist"
    ],
    "has_breakout_score": false,
    "has_futures_impulse_score": false,
    "has_pullback_resume_score": false,
    "surface_top_keys": [
      "branch_id",
      "branch_ready",
      "breakout_acceptance",
      "breakout_accepted",
      "breakout_buffer_ok",
      "breakout_extension",
      "breakout_not_overextended",
      "breakout_ref",
      "breakout_shelf_high",
      "breakout_shelf_low",
      "breakout_shelf_mid",
      "breakout_shelf_missing_reason",
      "breakout_shelf_snapshot_count",
      "breakout_shelf_valid",
      "breakout_shelf_width",
      "breakout_shelf_width_pct",
      "breakout_trigger",
      "breakout_triggered",
      "context_features",
      "context_pass",
      "continuation_support",
      "cross_option_context",
      "doctrine_id",
      "eligible",
      "entry_mode_hint",
      "failed_stage",
      "fallback_features",
      "fallback_ready",
      "family_id",
      "feature_refs",
      "futures_bias_ok",
      "futures_features",
      "near_same_side_wall",
      "oi_bias_alignment",
      "oi_wall_context",
      "option_features",
      "option_tradability_pass",
      "passed_stages",
      "premium_health",
      "present",
      "primary_features",
      "provider_ready",
      "regime",
      "regime_surface",
      "rich_surface",
      "runtime_mode",
      "runtime_mode_surface",
      "same_side_wall_strength_score",
      "selected_features",
      "setup_score",
      "shelf_confirmed",
      "shelf_valid",
      "shelf_width",
      "side",
      "strike_surface",
      "surface_kind",
      "tradability",
      "tradability_surface",
      "trend_score",
      "trend_score_ok"
    ],
    "tradability_ok": false
  },
  "misc_call": {
    "branch_id": "CALL",
    "candidate_source_keys_available": {
      "cvd_delta": 0.0,
      "delta_3": 0.0,
      "direction_score": 0.0,
      "event_rate_spike_ratio": 0.0,
      "trend_score": 0.0,
      "velocity_ratio": 0.0,
      "volume_norm": 0.0,
      "vwap_alignment_call": true,
      "vwap_alignment_put": true,
      "weighted_ofi": 0.0,
      "weighted_ofi_persist": 0.0
    },
    "eligible": false,
    "family_id": "MISC",
    "futures_features_keys": [
      "age_ms",
      "ask",
      "ask_qty",
      "ask_qty_5",
      "bearish_flow_ok",
      "best_ask",
      "best_bid",
      "bid",
      "bid_qty",
      "bid_qty_5",
      "book_present",
      "book_pressure",
      "bullish_flow_ok",
      "context_score",
      "contradiction_score_call",
      "contradiction_score_put",
      "cvd_delta",
      "delta_3",
      "depth_total",
      "direction_label",
      "direction_score",
      "ema21_slope",
      "ema9_slope",
      "event_rate_spike_ratio",
      "fresh",
      "instrument_key",
      "instrument_token",
      "liquidity_ok",
      "live_present",
      "ltp",
      "metadata_present",
      "mid_price",
      "nof_slope",
      "present",
      "provider_id",
      "quote_present",
      "raw",
      "role",
      "role_label",
      "runtime_mode",
      "source_label",
      "source_member_key",
      "spread",
      "spread_ratio",
      "stale",
      "timestamp_present",
      "touch_depth",
      "trading_symbol",
      "trend_score",
      "ts_event_ns",
      "ts_local_ns",
      "valid",
      "velocity_ratio",
      "volume",
      "volume_norm",
      "vwap_alignment_call",
      "vwap_alignment_put",
      "vwap_distance",
      "vwap_distance_ratio",
      "weighted_ofi",
      "weighted_ofi_persist"
    ],
    "has_breakout_score": false,
    "has_futures_impulse_score": false,
    "has_pullback_resume_score": false,
    "surface_top_keys": [
      "branch_id",
      "branch_ready",
      "breakout_acceptance",
      "breakout_event_id",
      "breakout_extension_pct",
      "breakout_ref",
      "breakout_trigger",
      "compression_detected",
      "compression_detection",
      "compression_event_id",
      "compression_high",
      "compression_low",
      "compression_mid",
      "compression_missing_reason",
      "compression_snapshot_count",
      "compression_valid",
      "compression_width",
      "compression_width_pct",
      "context_features",
      "context_pass",
      "cross_option_context",
      "directional_bias_ok",
      "directional_breakout_triggered",
      "doctrine_id",
      "eligible",
      "entry_mode_hint",
      "expansion_accepted",
      "failed_stage",
      "fallback_features",
      "fallback_ready",
      "family_id",
      "feature_refs",
      "full_retest",
      "futures_features",
      "hesitation_elapsed_sec",
      "hesitation_retest",
      "near_same_side_wall",
      "oi_bias_alignment",
      "oi_wall_context",
      "option_features",
      "option_tradability_pass",
      "passed_stages",
      "prebreak_distance",
      "prebreak_proximity_ok",
      "premium_health",
      "premium_health_ok",
      "present",
      "primary_features",
      "provider_ready",
      "regime",
      "regime_surface",
      "resume_confirmed",
      "retest_depth_pct",
      "retest_elapsed_sec",
      "retest_hold_ok",
      "retest_monitor_active",
      "retest_monitor_alive",
      "retest_monitor_started_ts_ms",
      "retest_timeout_sec",
      "retest_type",
      "retest_volume_ratio",
      "rich_surface",
      "runtime_mode",
      "runtime_mode_surface",
      "same_side_wall_strength_score",
      "selected_features",
      "setup_score",
      "side",
      "strike_surface",
      "surface_kind",
      "tradability",
      "tradability_surface"
    ],
    "tradability_ok": false
  },
  "misc_put": {
    "branch_id": "PUT",
    "candidate_source_keys_available": {
      "cvd_delta": 0.0,
      "delta_3": 0.0,
      "direction_score": 0.0,
      "event_rate_spike_ratio": 0.0,
      "trend_score": 0.0,
      "velocity_ratio": 0.0,
      "volume_norm": 0.0,
      "vwap_alignment_call": true,
      "vwap_alignment_put": true,
      "weighted_ofi": 0.0,
      "weighted_ofi_persist": 0.0
    },
    "eligible": false,
    "family_id": "MISC",
    "futures_features_keys": [
      "age_ms",
      "ask",
      "ask_qty",
      "ask_qty_5",
      "bearish_flow_ok",
      "best_ask",
      "best_bid",
      "bid",
      "bid_qty",
      "bid_qty_5",
      "book_present",
      "book_pressure",
      "bullish_flow_ok",
      "context_score",
      "contradiction_score_call",
      "contradiction_score_put",
      "cvd_delta",
      "delta_3",
      "depth_total",
      "direction_label",
      "direction_score",
      "ema21_slope",
      "ema9_slope",
      "event_rate_spike_ratio",
      "fresh",
      "instrument_key",
      "instrument_token",
      "liquidity_ok",
   
```

## Functions containing score terms
### app/mme_scalpx/services/features.py
- {'name': '_optional_provider_id', 'start': 538, 'end': 549, 'terms': ['surface']}
- {'name': '_batch26f_misr_zone_registry_from_sources', 'start': 1037, 'end': 1055, 'terms': ['surface']}
- {'name': '_batch26g_miso_microstructure_option_surface', 'start': 1059, 'end': 1120, 'terms': ['surface']}
- {'name': '_batch26o16_surface_for_branch', 'start': 3747, 'end': 3773, 'terms': ['surface']}
- {'name': '_batch26o16_normalize_family_frames', 'start': 3776, 'end': 3837, 'terms': ['family_frames', 'surface']}
- {'name': '_batch26o16_build_consumer_view', 'start': 3840, 'end': 3930, 'terms': ['family_frames', 'surface']}
- {'name': '_batch26e_misc_state_context', 'start': 4335, 'end': 4351, 'terms': ['surface']}
- {'name': '_batch7_surface_present', 'start': 4354, 'end': 4359, 'terms': ['surface']}
- {'name': '_batch7_patch_stage_flags', 'start': 4596, 'end': 4679, 'terms': ['surface']}
- {'name': '_batch7_snapshot_block', 'start': 4868, 'end': 4914, 'terms': ['selected_option_snapshot_ns']}
- {'name': '_batch25l_option_surface_kw_compat', 'start': 5427, 'end': 5650, 'terms': ['surface']}
- {'name': '_batch25l_futures_surface_feed_json_compat', 'start': 5665, 'end': 5747, 'terms': ['surface']}
- {'name': '_batch25l_family_branch_surface_restored', 'start': 5760, 'end': 5834, 'terms': ['surface.setdefault', 'surface']}
- {'name': '_batch25l_family_surface_restored', 'start': 5837, 'end': 5896, 'terms': ['surface.setdefault', 'surface']}
- {'name': '_batch25l_family_surfaces_restored', 'start': 5899, 'end': 5944, 'terms': ['surface']}
- {'name': '_batch25l_family_branch_surface_kind_normalized', 'start': 5960, 'end': 5991, 'terms': ['surface']}
- {'name': '_batch25m_contract_families_branch_strict', 'start': 6043, 'end': 6212, 'terms': ['surface']}
- {'name': '_batch26h_expected_branch_surface_kind', 'start': 6231, 'end': 6232, 'terms': ['surface']}
- {'name': '_batch26h_expected_family_surface_kind', 'start': 6235, 'end': 6236, 'terms': ['surface']}
- {'name': '_batch26h_finalize_branch_surface', 'start': 6239, 'end': 6258, 'terms': ['surface']}
- {'name': '_batch26h_finalize_family_surface', 'start': 6261, 'end': 6299, 'terms': ['surface']}
- {'name': '_batch26h_final_family_branch_surface', 'start': 6302, 'end': 6323, 'terms': ['surface']}
- {'name': '_batch26h_final_family_surface', 'start': 6326, 'end': 6359, 'terms': ['surface']}
- {'name': '_batch26h_final_family_surfaces', 'start': 6362, 'end': 6438, 'terms': ['surface']}
- {'name': '_batch26o17a_sanitize_selected_option', 'start': 7124, 'end': 7140, 'terms': ['response_efficiency', 'delta_3']}
- {'name': '_batch26o17b_sanitize_selected_option', 'start': 7295, 'end': 7311, 'terms': ['response_efficiency', 'delta_3']}
- {'name': '_batch26o17b_sanitize_common', 'start': 7314, 'end': 7333, 'terms': ['selected_option_rich']}
- {'name': '_batch26o20r3a_sanitize_selected_option', 'start': 7492, 'end': 7508, 'terms': ['response_efficiency', 'delta_3']}
- {'name': '_batch26o20r3a_sanitize_family_features_payload', 'start': 7511, 'end': 7532, 'terms': ['selected_option_rich']}
- {'name': '_r38zb_repair_classic_failover_family_features', 'start': 8284, 'end': 8367, 'terms': ['selected_option_snapshot_ns']}
### app/mme_scalpx/services/strategy_family/mist.py
- {'name': '_batch26d_required_common_surface', 'start': 228, 'end': 275, 'terms': ['surface']}
- {'name': 'extract_family_surface', 'start': 499, 'end': 513, 'terms': ['surface']}
- {'name': 'extract_provider_runtime', 'start': 524, 'end': 525, 'terms': ['surface']}
- {'name': 'selected_option', 'start': 539, 'end': 549, 'terms': ['surface']}
- {'name': 'trend_direction_ok', 'start': 561, 'end': 573, 'terms': ['delta_3', 'weighted_ofi', 'surface']}
- {'name': 'futures_impulse_score', 'start': 576, 'end': 584, 'terms': ['futures_impulse_score', 'velocity_ratio', 'surface']}
- {'name': 'option_confirmation_score', 'start': 587, 'end': 601, 'terms': ['option_confirmation_score', 'response_efficiency', 'delta_3', 'surface']}
- {'name': 'pullback_resume_score', 'start': 604, 'end': 623, 'terms': ['pullback_resume_score', 'surface']}
- {'name': 'context_score', 'start': 626, 'end': 646, 'terms': ['surface']}
- {'name': 'compute_score', 'start': 658, 'end': 686, 'terms': ['futures_impulse_score', 'pullback_resume_score', 'option_confirmation_score', 'surface']}
- {'name': 'evaluate_branch', 'start': 722, 'end': 874, 'terms': ['futures_impulse_score', 'option_confirmation_score', 'surface']}
- {'name': '_batch26_oi_c_has_oi_context', 'start': 1243, 'end': 1274, 'terms': ['surface']}
- {'name': 'context_score', 'start': 1288, 'end': 1310, 'terms': ['surface']}
### app/mme_scalpx/services/strategy_family/misb.py
- {'name': '_batch26d_required_common_surface', 'start': 210, 'end': 257, 'terms': ['surface']}
- {'name': 'consumer_view_to_mapping', 'start': 406, 'end': 439, 'terms': ['surface']}
- {'name': 'extract_family_surface', 'start': 474, 'end': 487, 'terms': ['surface']}
- {'name': 'extract_provider_runtime', 'start': 498, 'end': 499, 'terms': ['surface']}
- {'name': 'selected_option', 'start': 513, 'end': 521, 'terms': ['surface']}
- {'name': 'futures_bias_ok', 'start': 538, 'end': 554, 'terms': ['delta_3', 'weighted_ofi', 'velocity_ratio', 'surface']}
- {'name': 'breakout_trigger_score', 'start': 557, 'end': 581, 'terms': ['breakout_score', 'velocity_ratio', 'surface']}
- {'name': 'option_confirmation_score', 'start': 584, 'end': 607, 'terms': ['option_confirmation_score', 'response_efficiency', 'delta_3', 'surface']}
- {'name': 'context_score', 'start': 610, 'end': 625, 'terms': ['surface']}
- {'name': 'compute_score', 'start': 637, 'end': 664, 'terms': ['breakout_score', 'option_confirmation_score', 'surface']}
- {'name': 'evaluate_branch', 'start': 679, 'end': 825, 'terms': ['breakout_score', 'option_confirmation_score', 'surface']}
- {'name': '_batch26_oi_c_has_oi_context', 'start': 1194, 'end': 1225, 'terms': ['surface']}
- {'name': 'context_score', 'start': 1239, 'end': 1261, 'terms': ['surface']}
### app/mme_scalpx/services/strategy_family/misc.py
- {'name': '_batch26d_required_common_surface', 'start': 222, 'end': 269, 'terms': ['surface']}
- {'name': 'consumer_view_to_mapping', 'start': 433, 'end': 467, 'terms': ['surface']}
- {'name': 'extract_family_surface', 'start': 502, 'end': 515, 'terms': ['surface']}
- {'name': 'extract_provider_runtime', 'start': 526, 'end': 527, 'terms': ['surface']}
- {'name': 'selected_option', 'start': 535, 'end': 545, 'terms': ['surface']}
- {'name': 'directional_breakout_ok', 'start': 586, 'end': 598, 'terms': ['delta_3', 'weighted_ofi', 'surface']}
- {'name': 'compression_score', 'start': 601, 'end': 619, 'terms': ['surface']}
- {'name': 'breakout_score', 'start': 622, 'end': 642, 'terms': ['breakout_score', 'velocity_ratio', 'surface']}
- {'name': 'retest_resume_score', 'start': 645, 'end': 675, 'terms': ['surface']}
- {'name': 'option_confirmation_score', 'start': 678, 'end': 701, 'terms': ['option_confirmation_score', 'response_efficiency', 'delta_3', 'surface']}
- {'name': 'context_score', 'start': 704, 'end': 729, 'terms': ['surface']}
- {'name': 'compute_score', 'start': 741, 'end': 773, 'terms': ['breakout_score', 'option_confirmation_score', 'surface']}
- {'name': 'evaluate_branch', 'start': 781, 'end': 946, 'terms': ['breakout_score', 'option_confirmation_score', 'surface']}
- {'name': '_batch25o_find_misc_branch_frame', 'start': 1266, 'end': 1284, 'terms': ['surface']}
- {'name': '_batch26_oi_c_has_oi_context', 'start': 1393, 'end': 1424, 'terms': ['surface']}
- {'name': 'context_score', 'start': 1438, 'end': 1460, 'terms': ['surface']}
### app/mme_scalpx/services/strategy_family/misr.py
- {'name': '_batch26d_required_common_surface', 'start': 212, 'end': 259, 'terms': ['surface']}
- {'name': 'consumer_view_to_mapping', 'start': 410, 'end': 443, 'terms': ['surface']}
- {'name': 'extract_family_surface', 'start': 478, 'end': 491, 'terms': ['surface']}
- {'name': 'extract_provider_runtime', 'start': 502, 'end': 503, 'terms': ['surface']}
- {'name': 'selected_option', 'start': 517, 'end': 525, 'terms': ['surface']}
- {'name': 'active_zone', 'start': 528, 'end': 551, 'terms': ['surface']}
- {'name': 'reversal_direction_ok', 'start': 579, 'end': 591, 'terms': ['delta_3', 'weighted_ofi', 'surface']}
- {'name': 'reversal_structure_score', 'start': 594, 'end': 631, 'terms': ['surface']}
- {'name': 'option_confirmation_score', 'start': 634, 'end': 657, 'terms': ['option_confirmation_score', 'response_efficiency', 'delta_3', 'surface']}
- {'name': 'context_score', 'start': 660, 'end': 689, 'terms': ['surface']}
- {'name': 'compute_score', 'start': 701, 'end': 729, 'terms': ['option_confirmation_score', 'surface']}
- {'name': 'evaluate_branch', 'start': 744, 'end': 912, 'terms': ['option_confirmation_score', 'surface']}
- {'name': 'active_zone', 'start': 969, 'end': 1032, 'terms': ['surface']}
- {'name': '_misr_oi_wall_context', 'start': 1035, 'end': 1082, 'terms': ['surface']}
- {'name': 'context_score', 'start': 1085, 'end': 1114, 'terms': ['surface']}
- {'name': '_batch26e_iter_children', 'start': 1449, 'end': 1479, 'terms': ['surface']}
- {'name': '_batch26_oi_c_has_oi_context', 'start': 2039, 'end': 2070, 'terms': ['surface']}
- {'name': 'context_score', 'start': 2084, 'end': 2106, 'terms': ['surface']}
### app/mme_scalpx/services/strategy_family/common.py
- {'name': '_validate_common_surface', 'start': 864, 'end': 967, 'terms': ['surface']}
- {'name': 'resolve_classic_runtime_mode', 'start': 1085, 'end': 1102, 'terms': ['surface']}
- {'name': 'resolve_miso_runtime_mode', 'start': 1106, 'end': 1120, 'terms': ['surface']}

## Extracted source files
- `run/audits/B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420_raw/features_context.txt`
- `run/audits/B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420_raw/mist_context.txt`
- `run/audits/B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420_raw/misb_context.txt`
- `run/audits/B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420_raw/misc_context.txt`
- `run/audits/B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420_raw/misr_context.txt`
- `run/audits/B1-PROFIT-LIVE-R39WC_DYNAMIC_SCORE_SURFACE_PATCH_PLAN_NO_PATCH_NO_START_NO_ORDER_exact_source_patch_plan_for_features_to_family_dynamic_score_alias_publication_20260603_140420_raw/common_context.txt`

## Next route
- If accepted, next batch should be a narrow additive patch in features.py only.
- Patch must add dynamic score alias publication, not threshold tuning.
- After patch: compile/import proof, then observe-only restart only if needed, then R39WA rerun.