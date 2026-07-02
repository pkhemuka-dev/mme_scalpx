# LANE-MIV-R3B_CONTENT_BASED_TICK_SURFACE_LOCATOR_AND_EVALUATOR_RUN_NO_SOURCE_PATCH_NO_REPLAY_NO_ORDER_locate_real_futures_selected_option_tick_or_feature_rows_by_content_then_run_miv_evaluator_without_replay_20260611_233308 Runbook

This batch fixes R3A's locator problem by scanning content, not filenames.

It may read:
- run/live_capture
- run/replay
- run/audits

It must not:
- run replay_run.py
- start services
- send orders
- mutate source
- mutate registries
- touch Redis or locks
