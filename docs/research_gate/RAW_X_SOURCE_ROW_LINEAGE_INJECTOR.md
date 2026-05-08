# RAW-X Repair Source-Row Lineage Field Injector

Date: 2026-05-01
Generated UTC: 2026-05-01T10:08:56.033391+00:00
Batch tag: batch_raw_x_repair_source_row_lineage_freeze_final_v2_20260501_153856

Purpose: repair the failed RAW-X command package and inject research-only family, side, strategy_id, and candidate_id lineage earlier in RAW/replay row enrichment.

This is replay/research-only. It does not trade, does not mutate live Redis truth, does not call brokers, and does not enable paper/live.
