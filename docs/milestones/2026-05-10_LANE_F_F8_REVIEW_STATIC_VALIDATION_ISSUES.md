# LANE-F-F8 — REVIEW_STATIC_VALIDATION_ISSUES

Created UTC: 2026-05-10T16:39:49.014932+00:00

Verdict: `REVIEW_F8_STATIC_TOKEN_REVIEW_NOT_CLEAN_NO_MUTATION`  
Classification: `F6_HELPER_STATIC_TOKEN_ISSUES_REQUIRE_REVIEW`

## Review
- F7 proof: `run/proofs/proof_lane_f_f7_static_validate_evidence_surface_patch_latest.json`
- F7 fail reasons: `['risk helper block contains forbidden token(s)', 'execution helper block contains forbidden token(s)']`
- compile_ok: `True`
- risk executable token hits: `[]`
- execution executable token hits: `[]`
- risk forbidden executable calls: `['get']`
- execution forbidden executable calls: `['get']`
- risk helper reference count: `1`
- execution helper reference count: `1`
- false_positive_confirmed: `False`
- fail_reasons: `['risk helper has forbidden executable call hits', 'execution helper has forbidden executable call hits']`

## Boundary
F8 does not mutate source, start services, write Redis, call brokers, send orders, run replay, run PnL, or admit a dataset.

## Next route
`F9_GUARDED_HELPER_SANITIZATION_OR_ROLLBACK_PLAN_NO_SERVICE_START`
