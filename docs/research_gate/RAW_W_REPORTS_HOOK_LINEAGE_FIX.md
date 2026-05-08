# RAW-W Reports Hook Lineage Fix

Date: 2026-05-01
Generated UTC: 2026-05-01T10:00:07.361424+00:00
Batch tag: batch_raw_w_reports_hook_lineage_fix_freeze_final_20260501_153007

Purpose: fix the RAW-S reports hook lineage path identified by RAW-V so research rows can derive family, side, strategy_id, and candidate_id from row/source lineage.

This is research/replay-only. It does not trade, does not mutate live Redis truth, does not call brokers, and does not enable paper/live.
