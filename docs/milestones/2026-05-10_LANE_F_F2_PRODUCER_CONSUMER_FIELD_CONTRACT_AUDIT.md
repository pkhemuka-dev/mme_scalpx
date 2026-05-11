# LANE-F-F2 — PRODUCER_CONSUMER_FIELD_CONTRACT_AUDIT

Created UTC: 2026-05-10T16:18:29.853850+00:00

Verdict: `REVIEW_F2_FIELD_CONTRACT_AUDIT_PRODUCER_REFERENCES_INCOMPLETE`  
Classification: `CONTRACT_SURFACE_AUDITED_DATASET_BUILD_NOT_READY`

## Baseline
F1 proof: `run/proofs/proof_lane_f_f1_trade_lifecycle_evidence_gap_audit_latest.json`  
F1 verdict: `PASS_F1_TRADE_LIFECYCLE_GAP_AUDIT_BLOCKED_AS_EXPECTED`  
F1 classification: `DATASET_ADMISSION_BLOCKED_TRUE_STRATEGY_RISK_APPROVED_LIFECYCLE_MISSING`

## Contract audit
Source files scanned: `841`  
Files with contract hits: `744`  
Missing required source references: `[]`  
Missing likely producer references: `['risk_decision_id', 'risk_status', 'risk_approval', 'risk_blockers']`

## Admission result
Current dataset remains **not admitted** for backtest/PnL.

## Next route
`F3_STRATEGY_RISK_BLOCKER_DIAGNOSTIC_BLUEPRINT_NO_PATCH_NO_LIVE_START`
