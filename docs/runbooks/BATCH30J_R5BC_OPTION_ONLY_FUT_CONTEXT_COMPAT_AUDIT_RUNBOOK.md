# Batch 30J-R5BC Runbook

Purpose:
Audit whether current replay code supports option-only futures context from `opt_ticks.jsonl.fut_ltp` when `fut_ticks.jsonl` is absent.

Proof:
`run/proofs/proof_batch30j_r5bc_option_only_fut_context_compat_audit_latest.json`

Option shape:
`run/audits/batch30j_r5bc_option_only_fut_context_compat_audit_20260510_120859/staging_opt_shape.json`

Code support classification:
`run/audits/batch30j_r5bc_option_only_fut_context_compat_audit_20260510_120859/code_support_classification.json`

Option-context contract:
`run/audits/batch30j_r5bc_option_only_fut_context_compat_audit_20260510_120859/option_context_contract_design_only.json`

Code scans:
`run/audits/batch30j_r5bc_option_only_fut_context_compat_audit_20260510_120859/code_scans.json`

Next:
Do not execute replay. Next safe path is R5BD design-only explicit compatibility patch plan or collect real fut_ticks.jsonl.
