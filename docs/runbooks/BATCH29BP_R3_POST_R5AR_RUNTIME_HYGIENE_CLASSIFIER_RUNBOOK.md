# Batch 29BP-R3 Runbook

Purpose:
After R5AR reported `runtime_clean=false`, classify exact runtime hygiene blocker before Lane C continues.

Proof:
`run/proofs/proof_batch29bp_r3_post_r5ar_runtime_hygiene_classifier_latest.json`

Runtime locks:
`run/audits/batch29bp_r3_post_r5ar_runtime_hygiene_classifier_20260510_112759/runtime_locks.json`

Runtime processes:
`run/audits/batch29bp_r3_post_r5ar_runtime_hygiene_classifier_20260510_112759/runtime_processes.json`

Findings:
`run/audits/batch29bp_r3_post_r5ar_runtime_hygiene_classifier_20260510_112759/runtime_findings.json`

PID files:
`run/audits/batch29bp_r3_post_r5ar_runtime_hygiene_classifier_20260510_112759/pidfiles.json`

Script inspection:
`run/audits/batch29bp_r3_post_r5ar_runtime_hygiene_classifier_20260510_112759/script_inspection.json`

Next:
Return to Lane C. Do not materialize R5AQ candidates; run R5AS row-level non-repo source discovery because R5AR proved 2026-05-08 was an export-date alias of existing 2026-04-17.
