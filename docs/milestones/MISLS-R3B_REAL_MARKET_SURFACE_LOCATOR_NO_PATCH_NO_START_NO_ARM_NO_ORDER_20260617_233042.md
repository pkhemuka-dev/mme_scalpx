# MISLS R3B Real Market Surface Locator

- timestamp: 2026-06-17T23:30:42+05:30
- mode: NO_PATCH_NO_START_NO_ARM_NO_ORDER
- purpose: locate real captured futures/options/tick/feature rows, excluding audit/proof/status JSON noise

## Safety environment
B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY=1
MME_OBSERVER=/home/Lenovo/scalpx/projects/mme_scalpx/bin/mme_live_observer.py
MME_PROJECT_ROOT=/home/Lenovo/scalpx/projects/mme_scalpx
MME_VENV_PY=/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python
SCALPX_OBSERVE_ONLY=1
=== COMPILE MISLS HELPERS ONLY ===
compile_rc=0
=== REAL MARKET SURFACE LOCATOR ===
locator_rc=0

## R3B compact summary
- verdict: PASS_MISLS_R3B_REAL_MARKET_SURFACE_FILES_LOCATED_NO_ORDER
- files_scanned_after_noise_exclusion: 2000
- rows_sampled_total: 18623

### Top market surface files
- run/replay_datasets/session_exports_quote_compat_day_filtered_20260425_155247/2026-04-20/ticks_mme_opt_stream.csv
  score= 16 rows= 200 research_candidates= 0 tradability= 200
  groups= {'futures': 200, 'option': 200, 'quality': 200, 'quote': 200}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 200), ('NO_SWEEP_LEVEL_TOUCH', 200), ('SIDE_UNKNOWN', 200), ('SPREAD_RATIO_MISSING', 200)]
- run/replay_datasets/session_exports_quote_compat_day_filtered_20260425_155247/2026-04-17/ticks_mme_fut_stream.csv
  score= 16 rows= 200 research_candidates= 0 tradability= 200
  groups= {'futures': 200, 'option': 200, 'quality': 200, 'quote': 200}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 200), ('NO_SWEEP_LEVEL_TOUCH', 200), ('SIDE_UNKNOWN', 200), ('SPREAD_RATIO_MISSING', 200)]
- run/replay_datasets/session_exports_quote_compat_day_filtered_20260425_155247/2026-04-20/ticks_mme_fut_stream.csv
  score= 16 rows= 200 research_candidates= 0 tradability= 200
  groups= {'futures': 200, 'option': 200, 'quality': 200, 'quote': 200}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 200), ('NO_SWEEP_LEVEL_TOUCH', 200), ('SIDE_UNKNOWN', 200), ('SPREAD_RATIO_MISSING', 200)]
- run/replay_datasets/session_exports_quote_compat_20260425_150651/2026-04-21/ticks_mme_opt_stream.csv
  score= 16 rows= 200 research_candidates= 0 tradability= 200
  groups= {'futures': 200, 'option': 200, 'quality': 200, 'quote': 200}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 200), ('NO_SWEEP_LEVEL_TOUCH', 200), ('SIDE_UNKNOWN', 200), ('SPREAD_RATIO_MISSING', 200)]
- run/replay_datasets/session_exports_quote_compat_20260425_150651/2026-04-21/ticks_mme_fut_stream.csv
  score= 16 rows= 200 research_candidates= 0 tradability= 200
  groups= {'futures': 200, 'option': 200, 'quality': 200, 'quote': 200}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 200), ('NO_SWEEP_LEVEL_TOUCH', 200), ('SIDE_UNKNOWN', 200), ('SPREAD_RATIO_MISSING', 200)]
- run/replay_datasets/session_exports_quote_compat_day_filtered_20260425_155247/2026-04-21/ticks_mme_opt_stream.csv
  score= 16 rows= 65 research_candidates= 0 tradability= 65
  groups= {'futures': 65, 'option': 65, 'quality': 65, 'quote': 65}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 65), ('NO_SWEEP_LEVEL_TOUCH', 65), ('SIDE_UNKNOWN', 65), ('SPREAD_RATIO_MISSING', 65)]
- run/replay_datasets/session_exports_quote_compat_day_filtered_20260425_155247/2026-04-21/ticks_mme_fut_stream.csv
  score= 16 rows= 12 research_candidates= 0 tradability= 12
  groups= {'futures': 12, 'option': 12, 'quality': 12, 'quote': 12}
  top_blockers= [('NO_RECLAIM_REJECT_CONFIRMATION', 12), ('NO_SWEEP_LEVEL_TOUCH', 12), ('SIDE_UNKNOWN', 12), ('SPREAD_RATIO_MISSING', 12)]
- run/research_capture/rcap_backfill_archive_doctor_20260418_demo/ticks_fut.parquet.jsonl
  score= 12 rows= 3 research_candidates= 0 tradability= 0
  groups= {'futures': 3, 'option': 3, 'quality': 3, 'quote': 3, 'time': 3}
  top_blockers= [('DEPTH_OR_QUOTE_QTY_MISSING', 3), ('NO_RECLAIM_REJECT_CONFIRMATION', 3), ('NO_SWEEP_LEVEL_TOUCH', 3), ('SPREAD_RATIO_MISSING', 3)]
- run/research_capture/rcap_run_archive_doctor_20260418_demo/ticks_fut.parquet.jsonl
  score= 12 rows= 3 research_candidates= 0 tradability= 0
  groups= {'futures': 3, 'option': 3, 'quality': 3, 'quote': 3, 'time': 3}
  top_blockers= [('DEPTH_OR_QUOTE_QTY_MISSING', 3), ('NO_RECLAIM_REJECT_CONFIRMATION', 3), ('NO_SWEEP_LEVEL_TOUCH', 3), ('SPREAD_RATIO_MISSING', 3)]
- run/research_capture/rcap_backfill_operational_20260418_greencheck/ticks_fut.parquet.jsonl
  score= 12 rows= 3 research_candidates= 0 tradability= 0
  groups= {'futures': 3, 'option': 3, 'quality': 3, 'quote': 3, 'time': 3}
  top_blockers= [('DEPTH_OR_QUOTE_QTY_MISSING', 3), ('NO_RECLAIM_REJECT_CONFIRMATION', 3), ('NO_SWEEP_LEVEL_TOUCH', 3), ('SPREAD_RATIO_MISSING', 3)]
- run/research_capture/rcap_run_operational_20260418_greencheck/ticks_fut.parquet.jsonl
  score= 12 rows= 3 research_candidates= 0 tradability= 0
  groups= {'futures': 3, 'option': 3, 'quality': 3, 'quote': 3, 'time': 3}
  top_blockers= [('DEPTH_OR_QUOTE_QTY_MISSING', 3), ('NO_RECLAIM_REJECT_CONFIRMATION', 3), ('NO_SWEEP_LEVEL_TOUCH', 3), ('SPREAD_RATIO_MISSING', 3)]
- run/research_capture/rcap_backfill_raw_20260418_greencheck/ticks_fut.parquet.jsonl
  score= 12 rows= 3 research_candidates= 0 tradability= 0
  groups= {'futures': 3, 'option': 3, 'quality': 3, 'quote': 3, 'time': 3}
  top_blockers= [('DEPTH_OR_QUOTE_QTY_MISSING', 3), ('NO_RECLAIM_REJECT_CONFIRMATION', 3), ('NO_SWEEP_LEVEL_TOUCH', 3), ('SPREAD_RATIO_MISSING', 3)]
=== PROCESS SAFETY SNAPSHOT ===

## R3B verdict
PASS_MISLS_R3B_REAL_MARKET_SURFACE_FILES_LOCATED_NO_ORDER

- compile_rc=0
- locator_rc=0
- runtime_started=NO
- paper_armed=NO
- order_attempted=NO
