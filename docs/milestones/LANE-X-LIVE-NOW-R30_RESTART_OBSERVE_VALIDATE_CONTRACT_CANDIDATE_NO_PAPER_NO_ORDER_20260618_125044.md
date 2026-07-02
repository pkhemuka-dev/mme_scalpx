# R30 Restart Observe Validate Contract + Candidate
- timestamp: 2026-06-18T12:50:44+05:30
- mode: OBSERVE_ONLY_NO_PAPER_NO_ORDER
- validates: R29B contract drift patch and candidate bridge
=== SAFETY BEFORE ===
=== MEMORY BEFORE ===
=== STOP OBSERVE SERVICES ONLY ===
=== START OBSERVE SERVICES WITH R29B CODE ===
=== WAIT 75S ===
=== VALIDATE CONTRACT + CANDIDATE BRIDGE ===
=== ERROR TAILS ONLY ===
--- feeds.stdout ---
--- features.stdout ---
--- strategy.stdout ---
=== FINAL PSTATUS ===
=== FINAL PROCESS ===
=== MEMORY AFTER ===

## R30 verdict
PASS_R30_CONTRACT_CLEAN_FRAMES_PRESENT_BRIDGE_OPEN_CANDIDATE_SEEN_NO_ORDER
- contract_error_present: False
- family_features_top_level_has_r20: False
- stream_has_family_frames_json: True
- family_frames_key_count: 10
- consumer_view: {'hold_only': False, 'mapping_repair': {'all_required_branch_keys': ['misb_call', 'misb_put', 'misc_call', 'misc_put', 'miso_call', 'miso_put', 'misr_call', 'misr_put', 'mist_call', 'mist_put'], 'batch': '26-O16', 'branch_frame_count': 10, 'miso_provider_ready_truth_preserved': False, 'missing_branch_keys': [], 'no_doctrine_evaluation': True, 'no_order_side_effect': True, 'no_threshold_relaxation': True}, 'provider_ready_classic': True, 'provider_ready_miso': False, 'r20_bridge_gate_mapping_repair': {'applied': True, 'candidate_forced': False, 'classic_ready': True, 'hold_only_after_repair': False, 'order_side_effect': False, 'safe_to_consume': True, 'selected_tradable': True, 'thresholds_changed': False}, 'safe_to_consume': True, 'tradability_ok': True}
- latest_decision: {'action': 'HOLD', 'activation_candidate_count': '1', 'activation_reason': 'candidate_observed_dry_run', 'candidate_present_shadow': '1', 'candidate_true_shadow': '1', 'family': None, 'reason': 'hold_only_family_features_consumer_bridge', 'side': 'FLAT'}
- xlen: {'decisions': 2061, 'execution': 0, 'features': 1701, 'orders': 0, 'risk': 0, 'trades': 0}
- validate_rc=0
- runtime_started=OBSERVE_ONLY_FEEDS_FEATURES_STRATEGY_ONLY
- paper_armed=NO
- order_attempted=NO
- redis_delete_attempted=NO
