# RAW-AA5 Existing Evidence Scale-up Discovery

created_at_utc: 2026-05-01T12:37:13.404392+00:00

## Verdict

- raw_aa5_freeze_final_ok: `True`
- discovery_verdict: `RAW_AA5_EXISTING_EVIDENCE_FOUND_BUT_NOT_PROMOTION_READY`
- recommendation: `NO_QUALIFIED_EXISTING_DATASET_COLLECT_LARGER_BALANCED_REPLAY_SAMPLE`
- validation_only: `true`
- patching_performed: `false`

## Thresholds

- min_trades: `300`
- min_trades_per_family: `30`
- max_unknown_family_ratio: `0.0`
- min_oi_wall_coverage: `0.8`

## Discovery counts

- candidate_file_count: `16`
- assessed_dataset_count: `16`
- qualified_dataset_count: `0`
- near_candidate_count: `1`

## Best dataset

- path: `run/replay/raw_x_repair_source_row_lineage_20260501_154627_post_fix_export/enriched_replay_records.jsonl`
- canonical_trade_rows: `2750`
- unknown_family_trade_ratio: `0.8109090909090909`
- min_family_trade_count: `104`
- oi_wall_coverage: `0.014909090909090908`

## Top ranked datasets

1. run/replay/raw_x_repair_source_row_lineage_20260501_154627_post_fix_export/enriched_replay_records.jsonl | trades=2750 | unknown=0.8109090909090909 | min_family=104 | oi_cov=0.014909090909090908 | qualified=False
2. run/replay/raw_x_repair_source_row_lineage_20260501_154325_post_fix_export/enriched_replay_records.jsonl | trades=2552 | unknown=0.8119122257053292 | min_family=96 | oi_cov=0.014890282131661442 | qualified=False
3. run/replay/raw_w_reports_hook_lineage_fix_20260501_153007_trade_family_backfill/trade_family_backfilled_records.jsonl | trades=1782 | unknown=0.7727272727272727 | min_family=81 | oi_cov=0.014029180695847363 | qualified=False
4. run/replay/raw_w_reports_hook_lineage_fix_20260501_153007_post_fix_export/enriched_replay_records.jsonl | trades=1782 | unknown=0.8148148148148148 | min_family=66 | oi_cov=0.014029180695847363 | qualified=False
5. run/replay/raw_x_repair_source_row_lineage_20260501_153856_post_fix_export/enriched_replay_records.jsonl | trades=1320 | unknown=0.8068181818181818 | min_family=51 | oi_cov=0.015151515151515152 | qualified=False
6. run/replay/raw_x_repair_source_row_lineage_20260501_154949_post_fix_export/enriched_replay_records.jsonl | trades=1201 | unknown=0.8084929225645295 | min_family=46 | oi_cov=0.01498751040799334 | qualified=False
7. run/replay/raw_y_small_validation_20260501_155332_trade_family_backfill/trade_family_backfilled_records.jsonl | trades=88 | unknown=0.0 | min_family=4 | oi_cov=0.022727272727272728 | qualified=False
8. run/replay/raw_t_post_raw_s_replay_rerun_20260501_151908_trade_family_backfill/trade_family_backfilled_records.jsonl | trades=528 | unknown=0.7727272727272727 | min_family=24 | oi_cov=0.015151515151515152 | qualified=False
9. run/replay/raw_t_post_raw_s_replay_rerun_20260501_151908_raw_s_export/enriched_replay_records.jsonl | trades=528 | unknown=0.8295454545454546 | min_family=18 | oi_cov=0.015151515151515152 | qualified=False
10. run/replay/raw_t_post_raw_s_replay_rerun_20260501_151813_trade_family_backfill/trade_family_backfilled_records.jsonl | trades=132 | unknown=0.7727272727272727 | min_family=6 | oi_cov=0.015151515151515152 | qualified=False

## Safety

No live runtime, broker IO, Redis live writes, order sending, strategy/risk/execution mutation, or paper/live enablement.
