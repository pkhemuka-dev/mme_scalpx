# RAW-Q Replay Trade-Row Family Backfill

Date: 2026-05-01
Generated UTC: 2026-05-01T09:03:25.557940+00:00
Batch tag: batch_raw_q_trade_family_backfill_freeze_final_20260501_143325

Purpose: backfill family/side/strategy_id on closed-trade rows using nearby candidate, decision, source artifact, and source-run lineage.

This is replay-only evidence work. It does not touch live runtime, brokers, Redis, orders, risk, execution, strategy, or paper/live enablement.
