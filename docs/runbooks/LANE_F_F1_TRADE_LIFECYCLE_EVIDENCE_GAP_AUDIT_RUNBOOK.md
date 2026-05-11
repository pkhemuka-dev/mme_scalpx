# LANE F F1 TRADE_LIFECYCLE_EVIDENCE_GAP_AUDIT Runbook

Purpose: classify the current trade-lifecycle evidence gap without patching code, starting services, writing Redis, sending orders, running replay, or running PnL/economics.

Inputs:
- `run/proofs/LATEST_REPLAY_DATA_A81.txt` if present
- `run/proofs/proof_replay_data_a81*.json`
- supporting A67/A68/A79/A80 proofs if present
- local run/audit/report/replay metadata only

Outputs:
- `run/proofs/proof_lane_f_f1_trade_lifecycle_evidence_gap_audit_20260510_214510.json`
- `run/proofs/proof_lane_f_f1_trade_lifecycle_evidence_gap_audit_latest.json`
- `run/proofs/manifest_lane_f_f1_trade_lifecycle_evidence_gap_audit_latest.json`
- `run/proofs/sha256_lane_f_f1_trade_lifecycle_evidence_gap_audit_latest.txt`
- `docs/milestones/2026-05-10_LANE_F_F1_TRADE_LIFECYCLE_EVIDENCE_GAP_AUDIT.md`
- `run/status/LANE_F_F1_TRADE_LIFECYCLE_EVIDENCE_GAP_AUDIT.txt`

Safety:
- no service start/stop
- no Redis mutation
- no broker call
- no paper/live enablement
- no replay execution
- no PnL/economics evaluation
- no source patch

Next recommended batch:
`F2_PRODUCER_CONSUMER_FIELD_CONTRACT_AUDIT_NO_PATCH_NO_LIVE_START`
