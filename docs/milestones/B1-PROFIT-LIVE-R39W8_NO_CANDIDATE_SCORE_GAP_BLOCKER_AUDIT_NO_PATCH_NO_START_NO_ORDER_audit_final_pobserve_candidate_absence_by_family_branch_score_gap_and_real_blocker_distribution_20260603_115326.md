# B1-PROFIT-LIVE-R39W8_NO_CANDIDATE_SCORE_GAP_BLOCKER_AUDIT_NO_PATCH_NO_START_NO_ORDER_audit_final_pobserve_candidate_absence_by_family_branch_score_gap_and_real_blocker_distribution_20260603_115326

Classification: `PASS_R39W8_NO_CANDIDATE_BUT_REAL_SCORE_GAPS_AND_BLOCKERS_VISIBLE_NO_ORDER`

## Meaning
This is the focused A7 post-pobserve no-candidate audit. It does not run another observe window and does not patch/start/stop/delete/order.

## Safety
```text
orders:mme:stream=0
risk:mme:stream=0
execution:mme:stream=0
system:errors:stream=0
decisions:mme:stream=629
features:mme:stream=65
```

## Decision-level counts
- bundle_entry_count: 150
- current_entry_count: 300
- candidate_positive_count: 0
- classic_runtime_disabled_count: 0

### Decision reasons
- hold_only_family_features_consumer_bridge: 450

### Activation reasons
- no_candidate: 344
- view_data_invalid: 106

## Leaf/no-signal reasons
- score_below_threshold: 1376
- directional_breakout_not_confirmed: 688
- reversal_direction_not_confirmed: 688
- stage_provider_ready_miso_failed: 688

## Family + branch + reason
- MIST CALL / score_below_threshold: 344
- MIST PUT / score_below_threshold: 344
- MISB CALL / score_below_threshold: 344
- MISB PUT / score_below_threshold: 344
- MISC CALL / directional_breakout_not_confirmed: 344
- MISC PUT / directional_breakout_not_confirmed: 344
- MISR CALL / reversal_direction_not_confirmed: 344
- MISR PUT / reversal_direction_not_confirmed: 344
- MISO CALL / stage_provider_ready_miso_failed: 344
- MISO PUT / stage_provider_ready_miso_failed: 344

## Nearest misses by family/branch
- MISB CALL: reason=score_below_threshold score=0.35993846153846154 min_score=0.64 gap=0.2800615384615385 context=0.62 option=0.5 fut_impulse=None breakout=0.004615384615384616
- MISB PUT: reason=score_below_threshold score=0.19493846153846156 min_score=0.64 gap=0.44506153846153845 context=0.62 option=0.0 fut_impulse=None breakout=0.004615384615384616
- MIST CALL: reason=score_below_threshold score=0.2325 min_score=0.62 gap=0.38749999999999996 context=0.6 option=0.45 fut_impulse=0.0 breakout=None
- MIST PUT: reason=score_below_threshold score=0.12 min_score=0.62 gap=0.5 context=0.6 option=0.0 fut_impulse=0.0 breakout=None

## Top 20 nearest misses overall
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466026341-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466026007-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466025728-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466025454-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466025176-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466024851-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466024533-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466024225-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466020996-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466020725-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466020453-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466020175-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466019901-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466019605-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466019333-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466019062-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466018319-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466018042-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466017774-0
- MISB CALL score_below_threshold: score=0.35993846153846154 min=0.64 gap=0.2800615384615385 regime=LOWVOL decision=1780466017483-0

## View data invalid samples
- {'source': 'bundle', 'id': '1780466023954-0', 'data_valid': 0, 'provider_ready_classic': 0, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466023307646976}
- {'source': 'bundle', 'id': '1780466023720-0', 'data_valid': 0, 'provider_ready_classic': 0, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466023307646976}
- {'source': 'bundle', 'id': '1780466023487-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466023246-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466022996-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466022744-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466022485-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466022212-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466021962-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}
- {'source': 'bundle', 'id': '1780466021712-0', 'data_valid': 0, 'provider_ready_classic': 1, 'safe_to_consume': 1, 'reason': 'hold_only_family_features_consumer_bridge', 'activation_reason': 'view_data_invalid', 'features_generated_at_ns': 1780466020738603264}

## Next route
- If nearest misses are far from min_score, this was natural no-signal and not a live-readiness blocker.
- If nearest misses are close, continue observe-only until candidate-positive or run targeted candidate-threshold audit only; do not tune doctrine yet.
- If blocker export is insufficient, patch only blocker-reporting/export, not thresholds.
- Paper remains blocked until candidate-positive + safety preflight + explicit approval.