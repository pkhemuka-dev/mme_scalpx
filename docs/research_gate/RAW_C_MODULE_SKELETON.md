# RAW-C — Module Skeleton and Schemas

Date: 2026-05-01
Generated UTC: 2026-05-01T07:18:32.399199+00:00
Batch tag: batch_raw_c_module_skeleton_freeze_final_20260501_124832

## Purpose

Batch RAW-C creates the first RAW / Research Gate code owner.

This batch is intentionally limited to package skeleton, frozen constants, lightweight dataclass schemas, manifest helpers, read/write helpers, integrity helpers, and policy JSON files.

## Created package

- app/mme_scalpx/research_gate/__init__.py
- app/mme_scalpx/research_gate/contracts.py
- app/mme_scalpx/research_gate/models.py
- app/mme_scalpx/research_gate/manifest.py
- app/mme_scalpx/research_gate/reader.py
- app/mme_scalpx/research_gate/writer.py
- app/mme_scalpx/research_gate/integrity.py

## Created config

- etc/research_gate/raw_policy.json
- etc/research_gate/report_policy.json
- etc/research_gate/promotion_policy.json
- etc/research_gate/pnl_policy.json
- etc/research_gate/oi_wall_policy.json

## Preserved boundaries

RAW-C does not wire into live runtime.

RAW-C does not touch feeds, features, strategy, risk, execution, replay, research_capture, brokers, Redis, or strategy-family configs.

RAW-C does not compute PnL yet.

RAW-C does not analyze OI-wall yet.

RAW-C only establishes contracts and schemas for later batches.

## Verdict

PASS if proof JSON passes and imports/compile/static checks pass.
