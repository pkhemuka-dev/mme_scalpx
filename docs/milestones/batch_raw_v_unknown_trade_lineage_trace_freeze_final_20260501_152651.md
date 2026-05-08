# Milestone — Batch RAW-V Unknown Trade Lineage Trace

Date: 2026-05-01
Generated UTC: 2026-05-01T09:56:51.849610+00:00
Batch tag: batch_raw_v_unknown_trade_lineage_trace_freeze_final_20260501_152651

Achieved:
- Traced UNKNOWN-family trade rows to source artifacts.
- Produced unknown trade lineage map CSV.
- Produced producer patch target CSV.
- Produced source artifact summary CSV.
- Kept this batch review-only with no producer patch.
- Kept promotion and paper/live blocked.

Trace result:
- lineage_verdict: PATCH_TARGETS_IDENTIFIED
- trade_count: 528
- unknown_trade_count: 408
- unknown_trade_ratio: 0.772727
- producer_patch_target_count: 1

Top producer counts:
{
  "app/mme_scalpx/replay/reports.py or app/mme_scalpx/replay/artifacts.py": 408
}

Next:
Use producer_patch_targets.csv to patch the exact top producer function in the next batch; keep paper/live blocked.
