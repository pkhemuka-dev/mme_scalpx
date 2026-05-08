# Milestone — Batch RAW-T Post-RAW-S Replay Rerun

Date: 2026-05-01
Generated UTC: 2026-05-01T09:49:08.095399+00:00
Batch tag: batch_raw_t_post_raw_s_replay_rerun_freeze_final_20260501_151908

Achieved:
- Ran post-RAW-S replay evidence export mode.
- Reran RAW-N before trade-family backfill.
- Reran RAW-Q trade-family backfill.
- Reran RAW-N after trade-family backfill.
- Reran RAW-R family PnL/gap review.
- Compared baseline RAW-Q/R against post-RAW-S evidence.
- Kept promotion and paper/live blocked.

Before/after family coverage:
- baseline_unknown_family_ratio: 0.772727
- post_raw_s_unknown_family_ratio: 0.772727
- unknown_family_ratio_delta_after_minus_before: 0.0
- coverage_improved: False
- post_raw_s_trade_count: 528
- post_raw_s_known_family_trade_count: 120
- post_raw_s_unknown_family_trade_count: 408
- post_raw_s_rank_candidate_family_count: 5

RAW-Q after RAW-S:
- trade_family_before_count: 90
- trade_family_after_count: 120
- trade_backfilled_count: 30

Next:
If coverage improved, run larger multi-session replay-only batch. If not, patch deeper replay producer call sites.
