# Batch 30J-R5AR Runbook

Purpose:
Resolve true trading-date provenance from row-level `source_date` / `ts_event` before any staging materialization.

Proof:
`run/proofs/proof_batch30j_r5ar_true_trading_date_provenance_guard_latest.json`

Candidate inspections:
`run/audits/batch30j_r5ar_true_trading_date_provenance_guard_20260510_112504/candidate_inspections.json`

Export false-date candidates:
`run/audits/batch30j_r5ar_true_trading_date_provenance_guard_20260510_112504/export_false_candidates.json`

Safe claimed candidates:
`run/audits/batch30j_r5ar_true_trading_date_provenance_guard_20260510_112504/safe_claimed_candidates.json`

Safe resolved candidates:
`run/audits/batch30j_r5ar_true_trading_date_provenance_guard_20260510_112504/safe_resolved_candidates.json`

Next:
Stop Lane C. Run runtime hygiene classifier.
