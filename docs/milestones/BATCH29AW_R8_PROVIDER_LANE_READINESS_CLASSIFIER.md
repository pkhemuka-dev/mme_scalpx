# Batch 29AW-R8 — Provider Lane Readiness Classifier

generated_at_utc: 2026-05-05T09:30:15.664812+00:00
verdict: `DEFER_29AW_R8_PROVIDER_LANE_READINESS_CLASSIFIER`
provider_state: `ZERODHA_ONLY_READY_DHAN_INACTIVE`
readiness_verdict: `ZERODHA_ONLY_READY_DHAN_INACTIVE`
blockers: `['FEATURES_STOPPED_FALSE', 'OLD_PROOF_STACK_STOPPED_FALSE', 'FEATURES_INACTIVE_FALSE']`
warnings: `['FULL_PROVIDER_NOT_READY:ZERODHA_ONLY_READY_DHAN_INACTIVE', 'DHAN_LANES_INACTIVE_REQUIRES_SEPARATE_DHAN_LANE_REPAIR_OR_PROVIDER_SESSION_CHECK']`

## Purpose
Classify current direct feeds readiness by provider lane after negative-volume fix and feed relock.

## Safety
- No production patch.
- No service restart.
- No Redis restart.
- No paper/live enablement.
- No order sending.

## Next
REPAIR_LISTED_29AW_R8_HARD_BLOCKERS
