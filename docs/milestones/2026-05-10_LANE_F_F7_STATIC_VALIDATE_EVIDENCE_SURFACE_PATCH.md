# LANE-F-F7 — STATIC_VALIDATE_EVIDENCE_SURFACE_PATCH

Created UTC: 2026-05-10T16:38:32.156578+00:00

Verdict: `REVIEW_F7_STATIC_VALIDATION_FOUND_ISSUES_NO_MUTATION`  
Classification: `F6_EVIDENCE_SURFACE_PATCH_NEEDS_REVIEW`

## Validation
- F6 proof: `run/proofs/proof_lane_f_f6_guarded_risk_execution_evidence_surface_patch_latest.json`
- compile_ok: `True`
- risk block present: `True`
- execution block present: `True`
- risk helper present: `True`
- execution helper present: `True`
- risk missing fields: `[]`
- execution missing fields: `[]`
- risk forbidden tokens: `['broker', 'redis']`
- execution forbidden tokens: `['broker', 'redis']`
- risk integrated elsewhere: `False`
- execution integrated elsewhere: `False`
- fail reasons: `['risk helper block contains forbidden token(s)', 'execution helper block contains forbidden token(s)']`

## Boundary
F7 is static validation only. No service start, Redis write, replay, broker call, order send, PnL, or dataset admission occurred.

## Next route
`F8_REVIEW_STATIC_VALIDATION_ISSUES_NO_SERVICE_START_NO_REPLAY`
