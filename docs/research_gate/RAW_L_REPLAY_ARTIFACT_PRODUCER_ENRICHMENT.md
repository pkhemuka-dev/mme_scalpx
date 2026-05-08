# RAW-L — Replay Artifact Producer Enrichment Patch

Date: 2026-05-01
Generated UTC: 2026-05-01T08:27:03.224679+00:00
Batch tag: batch_raw_l_replay_artifact_enrichment_patch_freeze_final_20260501_135703

## Purpose

Batch RAW-L adds a replay-output enrichment stage that produces RAW-K-compatible enriched artifact copies.

It does not alter strategy doctrine. It does not change risk, execution, broker IO, live runtime, Redis, or paper/live settings.

## What this patch adds

- `app/mme_scalpx/replay/raw_artifact_enricher.py`
- `bin/replay_enrich_raw_artifacts.py`
- `etc/research_gate/replay_artifact_enrichment_policy.json`

The enricher reads existing replay/trade/candidate/decision artifacts and writes:

- `run/replay/raw_l_replay_enriched_20260501_135703/enriched_replay_records.jsonl`
- `run/replay/raw_l_replay_enriched_20260501_135703/enrichment_summary.json`
- `run/replay/raw_l_replay_enriched_20260501_135703/enrichment_manifest.json`

## RAW-K contract fields emitted

This patch emits all 45 RAW-K required fields.

Unknown evidence is not invented. Unknown values remain `UNKNOWN` or `null`.

## Boundaries

- no broker IO
- no Redis live writes
- no order sending
- no risk override
- no execution override
- no strategy mutation
- no live runtime mutation
- no paper/live enablement
- no research_capture mutation

## Important note

RAW-L is a safe replay-output enrichment stage. A later batch may wire this into replay runner/exporter flows after proof.
