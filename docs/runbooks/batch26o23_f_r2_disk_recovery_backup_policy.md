# 26-O23-F-R2 — disk-pressure recovery + backup-policy correction

- generated_at_utc: 2026-05-07T07:54:26.731526+00:00
- proof: `run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json`
- disk_recovery: `run/live_capture/batch26o23_f_r2_disk_recovery_backup_policy_20260507_132133/controlled_paper_o23f_r2_disk_recovery.json`
- backup_policy: `run/live_capture/batch26o23_f_r2_disk_recovery_backup_policy_20260507_132133/controlled_paper_o23f_r2_backup_policy.json`
- next_decision: `run/live_capture/batch26o23_f_r2_disk_recovery_backup_policy_20260507_132133/controlled_paper_o23f_r2_next_decision.json`
- backup_dir: `run/_code_backups/batch26o23_f_r2_disk_recovery_backup_policy_20260507_132133`

## Purpose
- Recover from `Errno 28 No space left on device` during O23-F-R1 backup.
- Clean only duplicate code-backup/cache surfaces.
- Freeze hash/slice backup policy for future bridge audits.
- No service start, no source patch, no order write, no real live.

## Disk recovery
```json
{
  "backup_policy": {
    "corrected_policy": [
      "Do not recursively copy old proof/live_capture artifacts into _code_backups.",
      "For previous JSON/proof artifacts, store sha256 + size + bounded head/tail slices only.",
      "For production source files under small limit, copy source backup.",
      "For large source/proof files, hash/slice only."
    ],
    "large_file_backup_policy": "hash_sha256_plus_head_tail_slice_only",
    "old_problem": "O23-F-R1 attempted full copy of proof/evidence files and failed with Errno 28 ENOSPC",
    "small_file_copy_limit_bytes": 250000
  },
  "batch": "26-O23-F-R2",
  "classification": "DISK_PRESSURE_RECOVERED_BACKUP_POLICY_CORRECTED",
  "disk_recovery": {
    "actions": [
      {
        "deleted": true,
        "mtime": 1778138465.2761784,
        "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/batch26o23_f_r1_memory_safe_bridge_audit_recovery_20260507_125104",
        "priority": 0,
        "reason": "duplicate_code_backup_dir_only",
        "relpath": "run/_code_backups/batch26o23_f_r1_memory_safe_bridge_audit_recovery_20260507_125104",
        "size_bytes": 4934504099
      },
      {
        "deleted": true,
        "mtime": 1778139868.9023058,
        "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/batch26o23_f_r1_memory_safe_bridge_audit_recovery_20260507_131428",
        "priority": 0,
        "reason": "duplicate_code_backup_dir_only",
        "relpath": "run/_code_backups/batch26o23_f_r1_memory_safe_bridge_audit_recovery_20260507_131428",
        "size_bytes": 261251072
      },
      {
        "deleted": true,
        "mtime": 1778135432.9880188,
        "path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/_code_backups/batch26o23_e_no_candidate_root_cause_review_20260507_115905",
        "priority": 10,
        "reason": "duplicate_code_backup_dir_only",
        "relpath": "run/_code_backups/batch26o23_e_no_candidate_root_cause_review_20260507_115905",
        "size_bytes": 4852638593
      }
    ],
    "after": {
      "df_h": {
        "cmd": "df -h . || true",
        "ok": true,
        "returncode": 0,
        "stderr": "",
        "stdout": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/root        78G   68G  9.4G  88% /\n"
      },
      "free_bytes": 10048937984,
      "free_gb": 9.359,
      "total_bytes": 83053432832,
      "used_bytes": 72987717632,
      "used_pct": 87.88
    },
    "before": {
      "df_h": {
        "cmd": "df -h . || true",
        "ok": true,
        "returncode": 0,
        "stderr": "",
        "stdout": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/root        78G   78G  364K 100% /\n"
      },
      "free_bytes": 372736,
      "free_gb": 0.0,
      "total_bytes": 83053432832,
      "used_bytes": 83036282880,
      "used_pct": 99.98
    },
    "deleted_bytes_estimate": 10048393764,
    "max_delete_bytes": 16106127360,
    "min_pass_free_bytes": 2147483648,
    "policy": {
      "deleted_only_duplicate_run_code_backups_and_cache_dirs": true,
      "did_not_delete_milestones_or_runbooks": true,
      "did_not_delete_run_live_capture": true,
      "did_not_delete_run_proofs": true,
      "did_not_delete_source_files": true
    },
    "target_free_bytes": 6442450944
  },
  "generated_at_utc": "2026-05-07T07:54:26.730346+00:00",
  "prior_o23f": {},
  "prior_o23f_r1": {},
  "runtime_snapshot": {
    "controlled_service_rows": [],
    "decisions_xlen": 1517,
    "features_xlen": 184,
    "latest_decisions_raw": {
      "cmd": "redis-cli XREVRANGE decisions:mme:stream + - COUNT 3",
      "ok": true,
      "returncode": 0,
      "stderr": "",
      "stdout": "ar\":true,\"selected_features\":{\"present\":false,\"side\":\"CALL\",\"provider_id\":null,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"entry_mode\":null,\"ltp\":null,\"best_bid\":null,\"best_ask\":null,\"mid\":null,\"spread\":null,\"spread_ratio\":null,\"spread_ticks\":null,\"bid_qty_5\":null,\"ask_qty_5\":null,\"depth_total\":null,\"volume\":null,\"ltq\":null,\"ltt_ns\":null,\"recent_ticks\":[],\"trade_ticks\":[],\"oi\":null,\"delta_proxy\":null,\"tick_size\":null,\"lot_size\":null,\"delta_3\":null,\"velocity_ratio\":null,\"weighted_ofi_persist\":null,\"response_efficiency\":0.0,\"impact_depth_fraction_one_lot\":null,\"packet_gap_ms\":null,\"ask_reloaded\":false,\"bid_reloaded\":false,\"raw\":{\"side\":\"CALL\",\"option_side\":\"CALL\",\"role\":\"SELECTED_CALL\"},\"metadata_present\":false,\"quote_present\":false,\"book_present\":false,\"timestamp_present\":false,\"live_present\":false,\"fresh\":false,\"stale\":true,\"tradability_ok\":false,\"valid\":true,\"option_side\":\"CALL\",\"role\":\"SELECTED_CALL\",\"option_token\":\"\",\"trading_symbol\":\"\"},\"option_features\":{\"present\":false,\"side\":\"CALL\",\"provider_id\":null,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"entry_mode\":null,\"ltp\":null,\"best_bid\":null,\"best_ask\":null,\"mid\":null,\"spread\":null,\"spread_ratio\":null,\"spread_ticks\":null,\"bid_qty_5\":null,\"ask_qty_5\":null,\"depth_total\":null,\"volume\":null,\"ltq\":null,\"ltt_ns\":null,\"recent_ticks\":[],\"trade_ticks\":[],\"oi\":null,\"delta_proxy\":null,\"tick_size\":null,\"lot_size\":null,\"delta_3\":null,\"velocity_ratio\":null,\"weighted_ofi_persist\":null,\"response_efficiency\":0.0,\"impact_depth_fraction_one_lot\":null,\"packet_gap_ms\":null,\"ask_reloaded\":false,\"bid_reloaded\":false,\"raw\":{\"side\":\"CALL\",\"option_side\":\"CALL\",\"role\":\"SELECTED_CALL\"},\"metadata_present\":false,\"quote_present\":false,\"book_present\":false,\"timestamp_present\":false,\"live_present\":false,\"fresh\":false,\"stale\":true,\"tradability_ok\":false,\"valid\":true,\"option_side\":\"CALL\",\"role\":\"SELECTED_CALL\",\"option_token\":\"\",\"trading_symbol\":\"\"},\"tradability_surface\":{\"present\":false,\"runtime_mode\":\"BASE_5DEPTH\",\"spread_ratio\":null,\"depth_total\":null,\"age_ms\":0.0,\"stale\":true,\"crossed_book\":true,\"queue_reload_veto\":false,\"impact_depth_fraction\":null,\"spread_ratio_max\":1.6,\"depth_min\":80,\"impact_depth_fraction_max\":0.27,\"futures_present\":false,\"futures_liquidity_pass\":false,\"futures_spread_ratio\":0.0,\"futures_depth_total\":0,\"spread_pass\":false,\"depth_pass\":false,\"stale_pass\":false,\"crossed_book_pass\":false,\"queue_pass\":true,\"impact_pass\":true,\"entry_pass\":false,\"blocked_reason\":\"not_present\",\"source_surface_key\":\"miso_call\",\"family_id\":\"MISO\",\"branch_id\":\"CALL\",\"side\":\"CALL\"},\"oi_wall_context\":{\"call\":{},\"put\":{},\"summary\":{\"present\":false,\"atm_reference_strike\":null,\"strike_step\":null,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall\":null,\"put_wall\":null,\"call_wall_distance_points\":null,\"put_wall_distance_points\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"call_wall_near\":false,\"put_wall_near\":false,\"total_call_oi\":0.0,\"total_put_oi\":0.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":null,\"oi_bias_score\":0.0,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false,\"oi_wall_ready\":false,\"near_any_wall\":false},\"oi_bias\":\"NEUTRAL\",\"law\":\"context_not_trigger\",\"wall_authority\":\"app.mme_scalpx.services.feature_family.strike_selection.build_oi_wall_summary\",\"canonical\":true},\"cross_option_context\":{\"call_minus_put_ltp\":null,\"call_put_depth_ratio\":null,\"call_put_spread_ratio\":null,\"call_present\":false,\"put_present\":false,\"selected_option_present\":false,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall_distance_pts\":null,\"put_wall_distance_pts\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"oi_bias\":\"NEUTRAL\",\"cross_option_ready\":false},\"rich_surface\":true}},\"miso_put\":{\"frame_id\":\"miso_put-1778129095363964343\",\"frame_ts_ns\":1778129095363964343,\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"side\":\"PUT\",\"runtime_mode\":\"DISABLED\",\"family_runtime_mode\":\"OBSERVE_ONLY\",\"active_futures_provider_id\":null,\"active_selected_option_provider_id\":null,\"active_option_context_provider_id\":null,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null,\"tick_size\":0.05,\"target_points\":5.0,\"stop_points\":4.0,\"eligible\":false,\"tradability_ok\":false,\"surface\":{\"surface_kind\":\"miso_branch\",\"present\":false,\"branch_ready\":false,\"family_id\":\"MISO\",\"doctrine_id\":\"MISO\",\"branch_id\":\"PUT\",\"burst_event_id\":null,\"burst_event_id_valid\":false,\"side\":\"PUT\",\"regime\":\"NORMAL\",\"runtime_mode\":\"DISABLED\",\"entry_mode_hint\":\"Dhan-mandatory strike ladder context\",\"provider_ready\":false,\"futures_features\":{\"present\":false,\"runtime_mode\":\"NORMAL\",\"source_label\":\"active_futures\",\"role_label\":\"classic_directional_truth\",\"instrument_key\":null,\"instrument_token\":null,\"provider_id\":null,\"ltp\":0.0,\"best_bid\":0.0,\"best_ask\":0.0,\"bid_qty_5\":0,\"ask_qty_5\":0,\"mid_price\":1e-08,\"spread\":0.0,\"spread_ratio\":0.0,\"touch_depth\":0,\"depth_total\":0,\"delta_3\":0.0,\"velocity_ratio\":0.0,\"weighted_ofi\":0.0,\"weighted_ofi_persist\":0.0,\"book_pressure\":0.5,\"vwap_distance\":0.0,\"vwap_distance_ratio\":0.0,\"ema9_slope\":0.0,\"ema21_slope\":0.0,\"event_rate_spike_ratio\":0.0,\"volume_norm\":0.0,\"cvd_delta\":0.0,\"nof_slope\":0.0,\"trend_score\":0.0,\"stale\":true,\"age_ms\":0.0,\"ts_event_ns\":0,\"ts_local_ns\":0,\"direction_score\":0.0,\"direction_label\":\"NEUTRAL\",\"bullish_flow_ok\":false,\"bearish_flow_ok\":false,\"vwap_alignment_call\":true,\"vwap_alignment_put\":true,\"contradiction_score_call\":-0.0,\"contradiction_score_put\":0.0,\"liquidity_ok\":false,\"context_score\":0.0,\"metadata_present\":false,\"quote_present\":false,\"book_present\":false,\"timestamp_present\":false,\"live_present\":false,\"fresh\":false,\"role\":\"active\"},\"primary_features\":{\"raw\":{}},\"context_features\":{},\"premium_health\":{},\"shadow_features\":{},\"microstructure\":{\"microstructure_present\":false,\"tick_count\":0,\"aggr_tick_count\":0,\"tape_tick_count\":0,\"persistence_tick_count\":0,\"window_start_ms\":0,\"window_end_ms\":0,\"aggressive_flow_ratio\":0.0,\"aggressive_flow_qty\":0.0,\"counter_flow_qty\":0.0,\"aggressive_trade_count\":0,\"counter_trade_count\":0,\"speed_of_tape\":0.0,\"imbalance_persist_score\":0.0,\"queue_reload_blocked\":false,\"queue_reload_clear\":true,\"queue_reload_score\":0.0,\"shadow_support_count\":0,\"shadow_live_count\":0,\"shadow_rows_seen\":0,\"shadow_support_ok\":false,\"aggression_ok\":false,\"tape_speed_ok\":false,\"imbalance_persist_ok\":false,\"live_flow_ok\":false,\"burst_event_id\":null,\"burst_event_id_valid\":false},\"strike_surface\":{\"present\":false,\"side\":\"PUT\",\"atm_reference_strike\":null,\"strike_step\":null,\"selected\":null,\"monitored\":[],\"tradable\":[],\"shadow\":[],\"nearest_same_side_wall\":null,\"near_same_side_wall\":false,\"same_side_wall_strength_score\":null,\"oi_bias\":\"NEUTRAL\",\"oi_bias_score\":0.0,\"oi_wall_summary\":{\"present\":false,\"atm_reference_strike\":null,\"strike_step\":null,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall\":null,\"put_wall\":null,\"call_wall_distance_points\":null,\"put_wall_distance_points\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"call_wall_near\":false,\"put_wall_near\":false,\"total_call_oi\":0.0,\"total_put_oi\":0.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":null,\"oi_bias_score\":0.0,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false,\"oi_wall_ready\":false,\"near_any_wall\":false},\"selection_mode_hint\":\"Dhan-mandatory strike ladder context\",\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false,\"oi_wall_ready\":false,\"chain_context_ready\":false,\"source_surface_key\":\"miso_put\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"ladder\":[],\"ladder_size\":0,\"ladder_surface\":{\"present\":false,\"row_count\":0,\"call_row_count\":0,\"put_row_count\":0,\"atm_reference_strike\":null,\"strike_step\":null,\"calls\":[],\"puts\":[],\"oi_wall_summary\":{\"present\":false,\"atm_reference_strike\":null,\"strike_step\":null,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall\":null,\"put_wall\":null,\"call_wall_distance_points\":null,\"put_wall_distance_points\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"call_wall_near\":false,\"put_wall_near\":false,\"total_call_oi\":0.0,\"total_put_oi\":0.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":null,\"oi_bias_score\":0.0,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false,\"oi_wall_ready\":false,\"near_any_wall\":false},\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false},\"oi_wall_context\":{\"call\":{},\"put\":{},\"summary\":{\"present\":false,\"atm_reference_strike\":null,\"strike_step\":null,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall\":null,\"put_wall\":null,\"call_wall_distance_points\":null,\"put_wall_distance_points\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"call_wall_near\":false,\"put_wall_near\":false,\"total_call_oi\":0.0,\"total_put_oi\":0.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":null,\"oi_bias_score\":0.0,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false,\"oi_wall_ready\":false,\"near_any_wall\":false},\"oi_bias\":\"NEUTRAL\",\"law\":\"context_not_trigger\",\"wall_authority\":\"app.mme_scalpx.services.feature_family.strike_selection.build_oi_wall_summary\",\"canonical\":true},\"nearest_call_oi_resistance\":{},\"nearest_put_oi_support\":{},\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall_strength\":0.0,\"put_wall_strength\":0.0},\"tradability\":{\"present\":false,\"runtime_mode\":\"BASE_5DEPTH\",\"spread_ratio\":null,\"depth_total\":null,\"age_ms\":0.0,\"stale\":true,\"crossed_book\":true,\"queue_reload_veto\":false,\"impact_depth_fraction\":null,\"spread_ratio_max\":1.6,\"depth_min\":80,\"impact_depth_fraction_max\":0.27,\"futures_present\":false,\"futures_liquidity_pass\":false,\"futures_spread_ratio\":0.0,\"futures_depth_total\":0,\"spread_pass\":false,\"depth_pass\":false,\"stale_pass\":false,\"crossed_book_pass\":false,\"queue_pass\":true,\"impact_pass\":true,\"entry_pass\":false,\"blocked_reason\":\"not_present\",\"source_surface_key\":\"miso_put\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"side\":\"PUT\"},\"regime_surface\":{\"present\":false,\"stale\":true,\"regime\":\"NORMAL\",\"regime_reason\":\"surface_unavailable\",\"regime_score\":0.0,\"velocity_ratio\":0.0,\"event_rate_spike_ratio\":0.0,\"volume_norm\":0.0,\"direction_score\":0.0,\"weighted_ofi\":0.0,\"spread_ratio\":0.0,\"futures_surface_present\":false,\"is_lowvol\":false,\"is_normal\":false,\"is_fast\":false,\"is_known\":false,\"cross_option_ready\":false},\"runtime_mode_surface\":{\"mode\":\"DISABLED\",\"runtime_mode\":\"DISABLED\",\"provider_ready\":false,\"depth20_ready\":false},\"strike_bundle_present\":false,\"selected_strike\":{},\"selected_strike_value\":null,\"selected_strike_score\":0.0,\"monitored\":[],\"tradable\":[],\"shadow\":[],\"shadow_support_count\":0,\"aggressive_flow_ratio\":0.0,\"speed_of_tape\":0.0,\"imbalance_persist_score\":0.0,\"queue_reload_score\":0.0,\"aggression_ok\":false,\"tape_speed_ok\":false,\"tape_urgency_ok\":false,\"imbalance_persist_ok\":false,\"persistence_ok\":false,\"live_flow_ok\":false,\"response_ok\":false,\"spread_ok\":true,\"depth_ok\":false,\"queue_reload_blocked\":false,\"queue_reload_clear\":true,\"queue_ok\":true,\"shadow_support_ok\":false,\"burst_detected\":false,\"burst_valid\":false,\"futures_vwap_align_ok\":true,\"futures_alignment_ok\":true,\"futures_contradiction_score\":1.0,\"futures_contradiction_blocked\":false,\"futures_veto_clear\":true,\"context_pass\":false,\"option_tradability_pass\":false,\"entry_eligibility\":false,\"oi_bias_alignment\":true,\"near_same_side_wall\":false,\"same_side_wall_strength_score\":0.0,\"setup_score\":0.18,\"risk_shell\":{\"target_points\":5.0,\"hard_stop_points\":4.0,\"disaster_stop_points\":5.0,\"ratchet_arm_points\":3.0,\"breakeven_plus_points\":0.5,\"entry_timeout_ms\":700.0,\"aggr_window_ms\":600.0,\"tape_window_ms\":600.0,\"persistence_window_ms\":600.0,\"max_hold_sec\":60.0,\"early_stall_sec\":30.0},\"feature_refs\":{\"fut_ltp\":0.0,\"fut_delta\":0.0,\"fut_velocity_ratio\":0.0,\"fut_weighted_ofi\":0.0,\"fut_weighted_ofi_persist\":0.0,\"fut_vwap_distance\":0.0,\"fut_volume_norm\":0.0,\"fut_direction_score\":0.0,\"fut_event_rate_spike_ratio\":0.0,\"opt_ltp\":0.0,\"opt_delta\":0.0,\"opt_velocity_ratio\":0.0,\"opt_weighted_ofi\":0.0,\"opt_weighted_ofi_persist\":0.0,\"opt_response_efficiency\":0.0,\"opt_context_score\":0.6,\"opt_spread_ratio\":0.0,\"opt_touch_depth\":0,\"opt_oi_bias\":\"UNKNOWN\",\"aggressive_flow_ratio\":0.0,\"speed_of_tape\":0.0,\"imbalance_persist_score\":0.0,\"queue_reload_score\":0.0,\"burst_event_id\":null},\"passed_stages\":[\"futures_vwap_alignment\",\"futures_contradiction_veto_clear\"],\"failed_stage\":\"runtime_disabled\",\"eligible\":false,\"batch9_freeze_blocked_reason\":\"runtime_disabled\",\"pre_batch9_failed_stage\":\"strike_bundle_present\",\"tradability_pass\":false,\"queue_clear\":true,\"futures_clear\":true,\"selected_features\":{\"present\":false,\"side\":\"PUT\",\"provider_id\":null,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"entry_mode\":null,\"ltp\":null,\"best_bid\":null,\"best_ask\":null,\"mid\":null,\"spread\":null,\"spread_ratio\":null,\"spread_ticks\":null,\"bid_qty_5\":null,\"ask_qty_5\":null,\"depth_total\":null,\"volume\":null,\"ltq\":null,\"ltt_ns\":null,\"recent_ticks\":[],\"trade_ticks\":[],\"oi\":null,\"delta_proxy\":null,\"tick_size\":null,\"lot_size\":null,\"delta_3\":null,\"velocity_ratio\":null,\"weighted_ofi_persist\":null,\"response_efficiency\":0.0,\"impact_depth_fraction_one_lot\":null,\"packet_gap_ms\":null,\"ask_reloaded\":false,\"bid_reloaded\":false,\"raw\":{\"side\":\"PUT\",\"option_side\":\"PUT\",\"role\":\"SELECTED_PUT\"},\"metadata_present\":false,\"quote_present\":false,\"book_present\":false,\"timestamp_present\":false,\"live_present\":false,\"fresh\":false,\"stale\":true,\"tradability_ok\":false,\"valid\":true,\"option_side\":\"PUT\",\"role\":\"SELECTED_PUT\",\"option_token\":\"\",\"trading_symbol\":\"\"},\"option_features\":{\"present\":false,\"side\":\"PUT\",\"provider_id\":null,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"entry_mode\":null,\"ltp\":null,\"best_bid\":null,\"best_ask\":null,\"mid\":null,\"spread\":null,\"spread_ratio\":null,\"spread_ticks\":null,\"bid_qty_5\":null,\"ask_qty_5\":null,\"depth_total\":null,\"volume\":null,\"ltq\":null,\"ltt_ns\":null,\"recent_ticks\":[],\"trade_ticks\":[],\"oi\":null,\"delta_proxy\":null,\"tick_size\":null,\"lot_size\":null,\"delta_3\":null,\"velocity_ratio\":null,\"weighted_ofi_persist\":null,\"response_efficiency\":0.0,\"impact_depth_fraction_one_lot\":null,\"packet_gap_ms\":null,\"ask_reloaded\":false,\"bid_reloaded\":false,\"raw\":{\"side\":\"PUT\",\"option_side\":\"PUT\",\"role\":\"SELECTED_PUT\"},\"metadata_present\":false,\"quote_present\":false,\"book_present\":false,\"timestamp_present\":false,\"live_present\":false,\"fresh\":false,\"stale\":true,\"tradability_ok\":false,\"valid\":true,\"option_side\":\"PUT\",\"role\":\"SELECTED_PUT\",\"option_token\":\"\",\"trading_symbol\":\"\"},\"tradability_surface\":{\"present\":false,\"runtime_mode\":\"BASE_5DEPTH\",\"spread_ratio\":null,\"depth_total\":null,\"age_ms\":0.0,\"stale\":true,\"crossed_book\":true,\"queue_reload_veto\":false,\"impact_depth_fraction\":null,\"spread_ratio_max\":1.6,\"depth_min\":80,\"impact_depth_fraction_max\":0.27,\"futures_present\":false,\"futures_liquidity_pass\":false,\"futures_spread_ratio\":0.0,\"futures_depth_total\":0,\"spread_pass\":false,\"depth_pass\":false,\"stale_pass\":false,\"crossed_book_pass\":false,\"queue_pass\":true,\"impact_pass\":true,\"entry_pass\":false,\"blocked_reason\":\"not_present\",\"source_surface_key\":\"miso_put\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"side\":\"PUT\"},\"oi_wall_context\":{\"call\":{},\"put\":{},\"summary\":{\"present\":false,\"atm_reference_strike\":null,\"strike_step\":null,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall\":null,\"put_wall\":null,\"call_wall_distance_points\":null,\"put_wall_distance_points\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"call_wall_near\":false,\"put_wall_near\":false,\"total_call_oi\":0.0,\"total_put_oi\":0.0,\"total_call_oi_change\":0.0,\"total_put_oi_change\":0.0,\"oi_ratio_put_to_call\":null,\"oi_bias_score\":0.0,\"oi_bias\":\"NEUTRAL\",\"ladder_present\":false,\"atm_reference_present\":false,\"wall_computable\":false,\"oi_wall_ready\":false,\"near_any_wall\":false},\"oi_bias\":\"NEUTRAL\",\"law\":\"context_not_trigger\",\"wall_authority\":\"app.mme_scalpx.services.feature_family.strike_selection.build_oi_wall_summary\",\"canonical\":true},\"cross_option_context\":{\"call_minus_put_ltp\":null,\"call_put_depth_ratio\":null,\"call_put_spread_ratio\":null,\"call_present\":false,\"put_present\":false,\"selected_option_present\":false,\"nearest_call_oi_resistance_strike\":null,\"nearest_put_oi_support_strike\":null,\"call_wall_distance_pts\":null,\"put_wall_distance_pts\":null,\"call_wall_strength_score\":null,\"put_wall_strength_score\":null,\"oi_bias\":\"NEUTRAL\",\"cross_option_ready\":false},\"rich_surface\":true}}},\"branch_frames\":{\"mist_call\":{\"key\":\"mist_call\",\"family_id\":\"MIST\",\"branch_id\":\"CALL\",\"side\":\"CALL\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"mist_put\":{\"key\":\"mist_put\",\"family_id\":\"MIST\",\"branch_id\":\"PUT\",\"side\":\"PUT\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"misb_call\":{\"key\":\"misb_call\",\"family_id\":\"MISB\",\"branch_id\":\"CALL\",\"side\":\"CALL\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"misb_put\":{\"key\":\"misb_put\",\"family_id\":\"MISB\",\"branch_id\":\"PUT\",\"side\":\"PUT\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"misc_call\":{\"key\":\"misc_call\",\"family_id\":\"MISC\",\"branch_id\":\"CALL\",\"side\":\"CALL\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"misc_put\":{\"key\":\"misc_put\",\"family_id\":\"MISC\",\"branch_id\":\"PUT\",\"side\":\"PUT\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"misr_call\":{\"key\":\"misr_call\",\"family_id\":\"MISR\",\"branch_id\":\"CALL\",\"side\":\"CALL\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"misr_put\":{\"key\":\"misr_put\",\"family_id\":\"MISR\",\"branch_id\":\"PUT\",\"side\":\"PUT\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"miso_call\":{\"key\":\"miso_call\",\"family_id\":\"MISO\",\"branch_id\":\"CALL\",\"side\":\"CALL\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null},\"miso_put\":{\"key\":\"miso_put\",\"family_id\":\"MISO\",\"branch_id\":\"PUT\",\"side\":\"PUT\",\"eligible\":false,\"tradability_ok\":false,\"instrument_key\":null,\"instrument_token\":null,\"option_symbol\":null,\"strike\":null,\"option_price\":null}}}\nactivation_report_json\n{\"activation_mode\":\"dry_run\",\"action\":\"HOLD\",\"hold\":true,\"promoted\":false,\"safe_to_promote\":false,\"reason\":\"view_data_invalid\",\"selected\":null,\"candidates\":[],\"blocked\":[],\"no_signal\":[],\"family_count\":5,\"branch_count\":2,\"metadata\":{\"gate\":\"global\",\"leaf_evaluation_skipped\":true,\"batch11_fail_closed\":true},\"strategy_report_only\":true,\"strategy_ts_ns\":1778129096780302054,\"live_orders_allowed\":false}\ndiagnostics_json\n{\"bridge\":\"strategy_family_consumer_bridge\",\"hold_only\":true,\"activation_bridge_report_only\":true,\"activation_mode\":\"dry_run\",\"activation_reason\":\"view_data_invalid\",\"activation_selected_family_id\":\"\",\"activation_selected_branch_id\":\"\",\"activation_candidate_count\":0,\"doctrine_leaves_observed\":true,\"doctrine_leaves_active\":false,\"broker_side_effects_allowed\":false,\"live_orders_allowed\":false,\"families\":[\"MIST\",\"MISB\",\"MISC\",\"MISR\",\"MISO\"],\"branch_frame_count\":10}\n"
    },
    "latest_orders_raw": {
      "cmd": "redis-cli XREVRANGE orders:mme:stream + - COUNT 5",
      "ok": true,
      "returncode": 0,
      "stderr": "",
      "stdout": "\n"
    },
    "observed_at_utc": "2026-05-07T07:54:26.296744+00:00",
    "orders_xlen": 0,
    "position": {},
    "risk_execution_rows": []
  }
}
```

## Verdict
- final_verdict: `PASS_O23_F_R2_DISK_RECOVERY_BACKUP_POLICY_OK_NO_REAL_LIVE`
- false_keys: `[]`
- next_recommended_batch: `26-O23-F-R3 memory-safe bridge audit retry with no full evidence copying, no service start, no real live.`

## Required verdicts
```json
{
  "backup_policy_json_written": true,
  "broker_call_false": true,
  "compile_pass": true,
  "did_not_delete_run_live_capture": true,
  "did_not_delete_run_proofs": true,
  "did_not_delete_source_files": true,
  "disk_cleanup_ran": true,
  "disk_free_above_min_pass": true,
  "disk_recovery_json_written": true,
  "forced_candidate_false": true,
  "import_pass": true,
  "next_decision_json_written": true,
  "no_controlled_pids_now": true,
  "o23e_pass_loaded": true,
  "order_write_false": true,
  "orders_zero_now": true,
  "position_flat_now": true,
  "production_source_patch_false": true,
  "real_live_approval_false": true,
  "risk_execution_not_running_now": true,
  "service_start_false": true,
  "threshold_relaxation_false": true
}
```