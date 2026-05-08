# Milestone — Batch RAW-W Reports Hook Lineage Fix

Date: 2026-05-01
Generated UTC: 2026-05-01T10:00:07.361424+00:00
Batch tag: batch_raw_w_reports_hook_lineage_fix_freeze_final_20260501_153007

Achieved:
- Strengthened RAW-S reports hook lineage helper.
- Added deterministic research-only candidate_id derivation.
- Preserved unresolved family/side/strategy_id as UNKNOWN.
- Marked derived fields with RAW-W lineage source metadata.
- Reran RAW-T-style comparison after the fix.
- Kept promotion and paper/live blocked.

Coverage result:
- baseline_unknown_family_ratio: 0.772727
- post_raw_w_unknown_family_ratio: 0.772727
- unknown_family_ratio_delta_after_minus_before: 0.0
- coverage_improved: False
- post_raw_w_trade_count: 1782
- post_raw_w_known_family_trade_count: 405
- post_raw_w_unknown_family_trade_count: 1377

Next:
If coverage improved, run larger multi-session replay-only validation. If not, trace source rows beyond the reports hook.
