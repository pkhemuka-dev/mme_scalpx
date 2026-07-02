# R28 Memory bump then R25 retry
- timestamp: 2026-06-18T11:28:27+05:30
- mode: OBSERVE_ONLY_NO_PAPER_NO_ORDER
- purpose: R24 code activation + stream family_frames validation after R27 safety restore
=== SAFETY BEFORE ===
=== REDIS MEMORY SAFE BUMP IF NEEDED / NO DELETE ===
=== STOP OBSERVE SERVICES ONLY ===
=== START OBSERVE SERVICES WITH R24 CODE ===
=== WAIT 45S ===
=== VALIDATE STREAM FRAMES + BRIDGE ===
=== ERROR TAILS ONLY ===
--- feeds.stdout ---
--- features.stdout ---
--- strategy.stdout ---
{"exc_info":"Traceback (most recent call last):\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1862, in start\n    self.run_once()\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1672, in run_once\n    bundle = self.bridge.read_feature_bundle()\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1300, in read_feature_bundle\n    return self._bundle_from_hash(raw)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1318, in _bundle_from_hash\n    FF_C.validate_family_features_payload(family_features)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 2283, in validate_family_features_payload\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: family_features top-level key drift: missing=[] extra=['r20_bridge_gate_mapping_repair']","level":"ERROR","logger":"app.mme_scalpx.services.strategy","message":"strategy_hold_bridge_loop_error","process":27522,"thread":"MainThread","ts":"2026-06-18T05:58:53.871253+00:00"}
{"exc_info":"Traceback (most recent call last):\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1862, in start\n    self.run_once()\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1672, in run_once\n    bundle = self.bridge.read_feature_bundle()\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1300, in read_feature_bundle\n    return self._bundle_from_hash(raw)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1318, in _bundle_from_hash\n    FF_C.validate_family_features_payload(family_features)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 2283, in validate_family_features_payload\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: family_features top-level key drift: missing=[] extra=['r20_bridge_gate_mapping_repair']","level":"ERROR","logger":"app.mme_scalpx.services.strategy","message":"strategy_hold_bridge_loop_error","process":27522,"thread":"MainThread","ts":"2026-06-18T05:59:17.147488+00:00"}
{"exc_info":"Traceback (most recent call last):\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1862, in start\n    self.run_once()\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1672, in run_once\n    bundle = self.bridge.read_feature_bundle()\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1300, in read_feature_bundle\n    return self._bundle_from_hash(raw)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/strategy.py\", line 1318, in _bundle_from_hash\n    FF_C.validate_family_features_payload(family_features)\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 2283, in validate_family_features_payload\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: family_features top-level key drift: missing=[] extra=['r20_bridge_gate_mapping_repair']","level":"ERROR","logger":"app.mme_scalpx.services.strategy","message":"strategy_hold_bridge_loop_error","process":27522,"thread":"MainThread","ts":"2026-06-18T05:59:25.819272+00:00"}
=== FINAL PSTATUS ===
=== FINAL PROCESS ===
=== MEMORY AFTER ===

## R28 verdict
REVIEW_R28_STREAM_FRAMES_PRESENT_BUT_BRIDGE_NOT_OPEN_NO_ORDER
- stream_has_family_frames_json: True
- family_frames_key_count: 10
- consumer_view: {'hold_only': True, 'mapping_repair': {'all_required_branch_keys': ['misb_call', 'misb_put', 'misc_call', 'misc_put', 'miso_call', 'miso_put', 'misr_call', 'misr_put', 'mist_call', 'mist_put'], 'batch': '26-O16', 'branch_frame_count': 10, 'miso_provider_ready_truth_preserved': False, 'missing_branch_keys': [], 'no_doctrine_evaluation': True, 'no_order_side_effect': True, 'no_threshold_relaxation': True}, 'provider_ready_classic': False, 'provider_ready_miso': False, 'r20_bridge_gate_mapping_repair': {'applied': True, 'candidate_forced': False, 'classic_ready': False, 'hold_only_after_repair': True, 'order_side_effect': False, 'safe_to_consume': False, 'selected_tradable': False, 'thresholds_changed': False}, 'safe_to_consume': False, 'tradability_ok': False}
- latest_decision: {'action': 'HOLD', 'activation_candidate_count': '1', 'activation_reason': 'candidate_observed_dry_run', 'candidate_present_shadow': '1', 'candidate_true_shadow': '1', 'reason': 'hold_only_family_features_consumer_bridge'}
- xlen: {'decisions': 5399, 'execution': 0, 'features': 1109, 'orders': 0, 'risk': 0, 'trades': 0}
- validate_rc=0
- runtime_started=OBSERVE_ONLY_FEEDS_FEATURES_STRATEGY_ONLY
- paper_armed=NO
- order_attempted=NO
- redis_delete_attempted=NO
