# RAW-V Unknown Trade Lineage Trace

Generated UTC: 2026-05-01T09:57:01.400783+00:00

## Verdict
- lineage_verdict: PATCH_TARGETS_IDENTIFIED
- promotion_allowed: False
- paper_live_allowed: False

## Coverage
- trade_count: 528
- unknown_trade_count: 408
- unknown_trade_ratio: 0.772727

## Producer counts
- app/mme_scalpx/replay/reports.py or app/mme_scalpx/replay/artifacts.py: 408

## Top patch targets
- app/mme_scalpx/replay/reports.py::_raw_s_emit_family_context unknown_trades=408 missing=candidate_id,family,side,strategy_id
  - Patch app/mme_scalpx/replay/reports.py:_raw_s_emit_family_context to emit family, side, strategy_id, candidate_id at original trade/candidate row creation time before RAW backfill.

## Governance
RAW-V is lineage trace only. No producer patching, no replay mutation, no paper/live enablement.
