# Lane X R16 Feature Sync Boundary Diagnostic

- timestamp: 2026-06-18T10:10:11+05:30
- mode: NO_PATCH_NO_ORDER
- purpose: diagnose why R15 had R11 refresh visible but feature sync false at ~1000ms skew
=== SAFETY CHECK ===
=== 45S SYNC SAMPLE LOOP ===
sample_rc=0
=== FEATURE SOURCE CONTEXT FOR SYNC RULE ===
=== MEMORY AND ERROR CHECK ===

## R16 verdict
PASS_R16_SYNC_BECAME_OK_DURING_SAMPLE_NO_PATCH_NO_ORDER
- last_sample: {'activation_candidate_count': None, 'active_fut_ns': 1781777454000000000, 'active_opt_ltp': '123.6', 'active_opt_ns': 1781777455000000000, 'active_opt_r11': 'applied', 'active_opt_symbol': 'NIFTY2662324100PE', 'active_skew_ms': 1000.0, 'decision_action': 'HOLD', 'decision_reason': 'no_candidate', 'feature_fut_ns': 1781777451000000000, 'feature_opt_ns': 1781777451000000000, 'feature_selected_ltp': 135.55, 'feature_skew_ms_calc': 0.0, 'feature_skew_ms_field': 0, 'feature_sync_ok': True, 'feature_valid': True, 'feature_validity': 'OK', 'feed_opt_ns': 1781777455000000000, 'provider_ready_classic': False, 'step': 14, 'tradability_ok': False}
- sample_rc=0
- source_patch_performed=NO
- runtime_start_requested=NO
- paper_armed=NO
- order_attempted=NO
