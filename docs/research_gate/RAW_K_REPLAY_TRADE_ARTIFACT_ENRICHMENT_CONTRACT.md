# RAW-K — Replay/Trade Artifact Enrichment Contract

Date: 2026-05-01
Generated UTC: 2026-05-01T07:54:09.009079+00:00
Batch tag: batch_raw_k_artifact_enrichment_contract_freeze_final_20260501_132409

## Purpose

Batch RAW-K freezes the replay/trade/candidate artifact enrichment contract.

This batch does **not** patch replay writers yet.

It defines the required fields and audits existing artifacts for gaps so the next patch can target replay/trade exporters cleanly.

## Why this batch exists

RAW-D through RAW-J proved the research system works, but also exposed promotion blockers:

- negative PnL evidence
- insufficient family labels
- insufficient blocker outcome labels
- OI-linked evidence not positive
- candidate/audit rows not clearly separated from executed trades

## Strict boundaries

- No replay module mutation.
- No research_capture mutation.
- No live runtime mutation.
- No broker IO.
- No Redis live writes.
- No order sending.
- No paper/live enablement.
- No strategy/risk/execution mutation.

## Required enrichment families

- identity fields
- strategy context fields
- candidate truth fields
- trade truth fields
- outcome label fields
- OI-wall context fields
- audit lineage fields

## Generated artifacts

- run/research_gate/raw_k_artifact_enrichment_20260501_132409/manifest.json
- run/research_gate/raw_k_artifact_enrichment_20260501_132409/artifact_enrichment_contract.json
- run/research_gate/raw_k_artifact_enrichment_20260501_132409/artifact_enrichment_gap_report.json
- run/research_gate/raw_k_artifact_enrichment_20260501_132409/artifact_enrichment_required_fields.csv
- run/research_gate/raw_k_artifact_enrichment_20260501_132409/artifact_enrichment_source_gap_matrix.csv
- run/research_gate/raw_k_artifact_enrichment_20260501_132409/RAW_K_ARTIFACT_ENRICHMENT_SUMMARY.md

## Next batch after RAW-K

Patch replay/trade/candidate artifact producers to emit the frozen enrichment fields.
