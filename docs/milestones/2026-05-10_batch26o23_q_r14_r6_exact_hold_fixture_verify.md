# 2026-05-10 — 26-O23-Q-R14-R6

Verdict: `PASS_O23_Q_R14_R6_EXACT_HOLD_FIXTURE_PROJECTION_VERIFIED`

## Purpose
Verify Q-R13 `family_scope_candidates_json` projection using an exact synthetic decision fixture satisfying the HOLD-only validator contract found in Q-R14-R5.

## Guard fixture values
- action: `HOLD`
- qty: `0`
- hold_only: `1`
- activation_report_only: `1`
- activation_action: `HOLD`
- activation_promoted: `0`
- activation_safe_to_promote: `0`
- live_orders_allowed: `0`

## Verification
- hold validator accepts exact fixture: `True`
- permissive publish projection ok: `True`
- real stream validator advisory ok: `False`
- projection verified: `True`

## Safety
- source_patch_applied: `False`
- source hash unchanged: `True`
- service_start_attempted: `False`
- paper_start_attempted: `False`
- real_live_attempted: `False`
- broker_call_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`

## Next
26-O23-Q-R15 source/consumer contract audit for family_scope_candidates_json; no paper/live, no risk/execution patch.
