# 26-O23-Q-A5F-R1 — Regime-Classifier Controlled-Paper Scope Selector

Generated UTC: 2026-05-11T08:34:55.048940+00:00

## Final verdict

`PASS_A5F_R1_REGIME_SCOPE_SELECTOR_READY_NO_ENABLEMENT`

## Classification

`PASS`

## Selected candidate

{
  "scope": "MISB:CALL",
  "family": "MISB",
  "side": "CALL",
  "selector_score": 14633100,
  "family_regime_score": 1461600,
  "scope_mentions": 17100,
  "matrix_row": {
    "blocker_count": 7500,
    "candidate_count": 6000,
    "dhan_context_ready_count": 0,
    "eligibility_count": 4000,
    "eligible_for_future_controlled_paper_review": true,
    "family": "MISB",
    "live_evidence_count": 10000,
    "no_signal_count": 7500,
    "not_eligible_reason": null,
    "owner_scope_count": 10000,
    "paper_approval": false,
    "provider_context_ready_count": 3500,
    "samples": [
      {
        "blocker_present": true,
        "blocker_reason_sample": "{\"surface_kind\": \"misb_family\", \"present\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"runtime_mode\": \"NORMAL\", \"regime\": \"NORMAL\", \"call\": {\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\"",
        "candidate_present": true,
        "dhan_context_ready_observed": false,
        "eligibility_present": true,
        "family": "MISB",
        "keys": [
          "branches",
          "call",
          "call_present",
          "call_ready",
          "call_setup_score",
          "doctrine_id",
          "dominant_branch",
          "dominant_ready_branch",
          "eligible",
          "family_id",
          "present",
          "put",
          "put_present",
          "put_ready",
          "put_setup_score",
          "regime",
          "regime_surface",
          "rich_surface",
          "runtime_mode",
          "runtime_mode_surface",
          "surface_kind"
        ],
        "no_signal_present": true,
        "owner_scope_present": true,
        "provider_context_ready_observed": true,
        "sample": "{\"surface_kind\": \"misb_family\", \"present\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"runtime_mode\": \"NORMAL\", \"regime\": \"NORMAL\", \"call\": {\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\", \"source_label\": \"active_futures\", \"role_label\": \"classic_directional_truth\", \"instrument_key\": null, \"instrument_token\": null, \"provider_id\": null, \"ltp\": 0.0, \"best_bid\": 0.0, \"best_ask\": 0.0, \"bid_qty_5\": 0, \"ask_qty_5\": 0, \"mid_price\": 1e-08, \"spread\": 0.0, \"spread_ratio\": 0.0, \"touch_depth\": 0, \"depth_total\": 0, \"delta_3\": 0.0, \"velocity_ratio\": 0.0, \"weighted_ofi\": 0.0, \"weighted_ofi_persis",
        "score": -0.19,
        "selected_option_ready_observed": false,
        "side": "CALL"
      },
      {
        "blocker_present": true,
        "blocker_reason_sample": "{\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\", \"source_label\": \"active_futures\", \"role_label\": \"classic_directional_truth\", \"instrument_key\": null, \"instrument_token\": null, \"provider_id\": null",
        "candidate_present": true,
        "dhan_context_ready_observed": false,
        "eligibility_present": true,
        "family": "MISB",
        "keys": [
          "batch9_freeze_blocked_reason",
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
          "pre_batch9_failed_stage",
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
        "no_signal_present": true,
        "owner_scope_present": true,
        "provider_context_ready_observed": true,
        "sample": "{\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\", \"source_label\": \"active_futures\", \"role_label\": \"classic_directional_truth\", \"instrument_key\": null, \"instrument_token\": null, \"provider_id\": null, \"ltp\": 0.0, \"best_bid\": 0.0, \"best_ask\": 0.0, \"bid_qty_5\": 0, \"ask_qty_5\": 0, \"mid_price\": 1e-08, \"spread\": 0.0, \"spread_ratio\": 0.0, \"touch_depth\": 0, \"depth_total\": 0, \"delta_3\": 0.0, \"velocity_ratio\": 0.0, \"weighted_ofi\": 0.0, \"weighted_ofi_persist\": 0.0, \"book_pressure\": 0.5, \"vwap_distance\": 0.0, \"vwap_distance_ratio\": 0.0, \"ema9_slope\": 0.0, \"ema21_slope\": 0.0, \"event_rate_spike_ratio\": 0.",
        "score": -1.0,
        "selected_option_ready_observed": false,
        "side": "CALL"
      },
      {
        "blocker_present": false,
        "blocker_reason_sample": null,
        "candidate_present": true,
        "dhan_context_ready_observed": false,
        "eligibility_present": false,
        "family": "MISB",
        "keys": [
          "atm_reference_present",
          "atm_reference_strike",
          "branch_id",
          "call_wall_strength",
          "candidates",
          "chain_context_ready",
          "family_id",
          "ladder",
          "ladder_present",
          "ladder_size",
          "ladder_surface",
          "near_same_side_wall",
          "nearest_call_oi_resistance",
          "nearest_call_oi_resistance_strike",
          "nearest_put_oi_support",
          "nearest_put_oi_support_strike",
          "nearest_same_side_wall",
          "oi_bias",
          "oi_bias_score",
          "oi_context_alignment",
          "oi_wall_context",
          "oi_wall_ready",
          "oi_wall_summary",
          "present",
          "put_wall_strength",
          "same_side_wall_strength_score",
          "selected",
          "selection_mode_hint",
          "side",
          "source_surface_key",
          "strike_step",
          "wall_computable"
        ],
        "no_signal_present": false,
        "owner_scope_present": true,
        "provider_context_ready_observed": false,
        "sample": "{\"present\": false, \"side\": \"CALL\", \"atm_reference_strike\": null, \"strike_step\": null, \"selected\": null, \"candidates\": [], \"nearest_same_side_wall\": null, \"near_same_side_wall\": false, \"same_side_wall_strength_score\": null, \"oi_bias\": \"NEUTRAL\", \"oi_bias_score\": 0.0, \"oi_context_alignment\": false, \"oi_wall_summary\": {\"present\": false, \"atm_reference_strike\": null, \"strike_step\": null, \"nearest_call_oi_resistance_strike\": null, \"nearest_put_oi_support_strike\": null, \"call_wall\": null, \"put_wall\": null, \"call_wall_distance_points\": null, \"put_wall_distance_points\": null, \"call_wall_strength_score\": null, \"put_wall_strength_score\": null, \"call_wall_near\": false, \"put_wall_near\": false, \"total_call_oi\": 0.0, \"total_put_oi\": 0.0, \"total_call_oi_change\": 0.0, \"total_put_oi_change\": 0.0, \"oi_ratio_put_to_call\": null, \"oi_bias_score\": 0.0, \"oi_bias\": \"NEUTRAL\", \"ladder_present\": false, \"atm_refer",
        "score": 0.0,
        "selected_option_ready_observed": false,
        "side": "CALL"
      },
      {
        "blocker_present": true,
        "blocker_reason_sample": "{\"present\": false, \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"thresholds\": {\"branch_id\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"degraded\": false, \"spread_ratio_max\": 1.6, \"depth_min\": 80, \"response_eff_min\": 0.17, \"impact_depth_fraction_max\": 0.27, \"liquidity_exit_spread_ratio\": 1.9, \"liquidity_exit_depth_fraction\": 0.6}, \"spread_ratio\": null, \"depth_total\": null, \"respo",
        "candidate_present": false,
        "dhan_context_ready_observed": false,
        "eligibility_present": false,
        "family": "MISB",
        "keys": [
          "age_ms",
          "blocked_reason",
          "branch_id",
          "crossed_book",
          "crossed_book_pass",
          "depth_pass",
          "depth_total",
          "entry_pass",
          "family_id",
          "impact_depth_fraction",
          "impact_pass",
          "liquidity_exit_trip",
          "present",
          "queue_pass",
          "queue_reload_veto",
          "regime",
          "response_efficiency",
          "response_pass",
          "runtime_mode",
          "selection_label",
          "side",
          "source_surface_key",
          "spread_pass",
          "spread_ratio",
          "stale",
          "stale_pass",
          "thresholds"
        ],
        "no_signal_present": true,
        "owner_scope_present": true,
        "provider_context_ready_observed": false,
        "sample": "{\"present\": false, \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"thresholds\": {\"branch_id\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"degraded\": false, \"spread_ratio_max\": 1.6, \"depth_min\": 80, \"response_eff_min\": 0.17, \"impact_depth_fraction_max\": 0.27, \"liquidity_exit_spread_ratio\": 1.9, \"liquidity_exit_depth_fraction\": 0.6}, \"spread_ratio\": null, \"depth_total\": null, \"response_efficiency\": 0.0, \"impact_depth_fraction\": null, \"age_ms\": 0.0, \"stale\": true, \"crossed_book\": true, \"queue_reload_veto\": false, \"spread_pass\": false, \"depth_pass\": false, \"response_pass\": false, \"impact_pass\": true, \"stale_pass\": false, \"crossed_book_pass\": false, \"queue_pass\": true, \"entry_pass\": false, \"liquidity_exit_trip\": true, \"blocked_reason\": \"not_present\", \"source_surface_key\": \"clas",
        "score": null,
        "selected_option_ready_observed": false,
        "side": "CALL"
      }
    ],
    "score_avg": -0.4655555555555601,
    "score_max": 0.0,
    "selected_option_ready_count": 0,
    "side": "CALL",
    "top_blocker_reasons": [
      {
        "count": 3585,
        "reason": "{\"present\": false, \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"thresholds\": {\"branch_id\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"degraded\": false, \"spread_ratio_max\": 1.6, \"depth_min\": 80, \"response_eff_min\": 0.17, \"impact_depth_fraction_max\": 0.27, \"liquidity_exit_spread_ratio\": 1.9, \"liquidity_exit_depth_fraction\": 0.6}, \"spread_ratio\": null, \"depth_total\": null, \"respo"
      },
      {
        "count": 2000,
        "reason": "{\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\", \"source_label\": \"active_futures\", \"role_label\": \"classic_directional_truth\", \"instrument_key\": null, \"instrument_token\": null, \"provider_id\": null"
      },
      {
        "count": 500,
        "reason": "{\"surface_kind\": \"misb_family\", \"present\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"runtime_mode\": \"NORMAL\", \"regime\": \"NORMAL\", \"call\": {\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\""
      },
      {
        "count": 500,
        "reason": "{\"CALL\": {\"surface_kind\": \"misb_branch\", \"present\": false, \"branch_ready\": false, \"family_id\": \"MISB\", \"doctrine_id\": \"MISB\", \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"entry_mode_hint\": \"Dhan-enhanced strike quality context only\", \"provider_ready\": false, \"futures_features\": {\"present\": false, \"runtime_mode\": \"NORMAL\", \"source_label\": \"active_futures\", \"role_label\": \"classic_directional_truth\", \"instrument_key\": null, \"instrument_token\": null, \"provider_"
      },
      {
        "count": 415,
        "reason": "{\"present\": false, \"branch_id\": \"CALL\", \"side\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"thresholds\": {\"branch_id\": \"CALL\", \"regime\": \"NORMAL\", \"runtime_mode\": \"NORMAL\", \"selection_label\": \"classic_call\", \"degraded\": false, \"spread_ratio_max\": 1.6, \"depth_min\": 80, \"response_eff_min\": 0.17, \"impact_depth_fraction_max\": 0.27, \"liquidity_exit_spread_ratio\": 1.9, \"liquidity_exit_depth_fraction\": 0.6}, \"spread_ratio\": 0.0, \"depth_total\": null, \"respon"
      }
    ]
  },
  "approval_phrase": "I_APPROVE_A5F_MISB_CALL_1LOT_CONTROLLED_PAPER_PREFLIGHT_ONLY_NO_REAL_LIVE",
  "paper_approval_now": false
}

## Blockers

[]

## Residual governance blockers

[
  "CONTROLLED_PAPER_STILL_BLOCKED_PENDING_SCOPE_SPECIFIC_CONTRACT_PREFLIGHT_DRYCHECK_AND_EXACT_APPROVAL",
  "REGIME_CLASSIFIER_IS_SELECTOR_ONLY_NOT_ORDER_AUTHORITY",
  "A5C_REMAINS_MIST_CALL_ONLY",
  "A5E_REMAINS_MISB_PUT_BACKUP_ONLY",
  "A5F_DID_NOT_START_RISK_OR_EXECUTION",
  "A5F_DID_NOT_CALL_BROKER",
  "A5F_DID_NOT_PLACE_ORDER",
  "REAL_LIVE_STILL_BLOCKED",
  "ALL_5_ORDER_CYCLE_TESTING_NOT_APPROVED"
]

## Next recommended batch

SEPARATE_MISB_CALL_CONTRACT_PREFLIGHT_PLAN_NO_ENABLEMENT

## Artifacts

- Proof: `run/proofs/proof_lane_a5f_r1_regime_scope_selector_20260511_135942.json`
- Latest proof: `run/proofs/proof_lane_a5f_r1_regime_scope_selector_latest.json`
- Selector: `run/audits/lane_a5f_r1_regime_scope_selector_20260511_135942_scope_selector.json`
- Audit: `run/audits/lane_a5f_r1_regime_scope_selector_20260511_135942.json`
- Runbook: `docs/runbooks/lane_a5f_r1_regime_scope_selector_20260511_135942_regime_selector_summary.md`
- SHA256: `run/proofs/sha256_lane_a5f_r1_regime_scope_selector_20260511_135942.txt`
