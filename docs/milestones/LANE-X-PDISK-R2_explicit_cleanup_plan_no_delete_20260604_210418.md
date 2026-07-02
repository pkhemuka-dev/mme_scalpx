# Lane X PDISK-R2 Cleanup Plan — NO DELETE YET

## Classification

PLAN_ONLY_NO_DELETE

## Current policy

Do not delete Day-4 Lane X evidence tonight. Disk has ~29G free, so no emergency cleanup is required.

## Protect — do not delete

### Day-4 Lane X source-of-truth

- run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_151929
- run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260604_203023
- run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260604_093504
- run/audits/LANE-X-R10_rolling_nearest_miss_sampler_20260604_100336_samples.csv
- run/audits/LANE-X-R11_final_live_close_window_sampler_20260604_152512_samples.csv
- run/proofs/LANE-X-*.json from 20260604
- docs/milestones/LANE-X-*.md from 20260604
- run/handoffs/LANE-X-*.md from 20260604

Reason: Day-4 is the current source of truth for R5P live validation, MIST response blocker, MISB shelf-width blocker, Dhan/MISO doctrine block, and helper fixes.

### Latest compact source bundle

- run/evidence_bundles/pdev_current.tar.gz
- run/evidence_bundles/pdev_current.tar.gz.sha256
- run/evidence_bundles/LATEST_PDEV_PACK.txt
- run/evidence_bundles/LATEST_PDEV_CURRENT_BUNDLE.txt

Reason: needed for future chat/source continuity.

### Governance artifacts

- run/proofs
- docs/milestones
- run/handoffs

Do not bulk-delete. Some subfolders are large, but proof governance depends on them.

## Defer / ask replay lane before deleting

These are huge but may be replay/backtest-grade or cross-lane source-of-truth:

- run/replay/staging/B3-R23_R37M_COMPACT_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER_export_time_aligned_compact_dataset_from_r37m_recorder_for_next_replay_20260528_220545/2026-05-27/decisions.jsonl
- run/replay/staging/B3-R23_R37M_COMPACT_REPLAY_DATASET_EXPORT_NO_PATCH_NO_REPLAY_NO_ORDER_export_time_aligned_compact_dataset_from_r37m_recorder_for_next_replay_20260528_220545/2026-05-27/features.jsonl
- run/replay/a58_feeds_features_execution
- run/replay/a61_feeds_features_strategy_execution
- run/replay/a64_feeds_features_strategy_risk_execution
- run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution
- run/replay/b3_r61d
- run/replay/staging

Reason: replay lane owns replay/staging cleanup authority.

## Good cleanup candidates after confirmation

### Candidate A — old A7 upload bundles already superseded

Small but safe after confirmation:

- run/evidence_bundles/A7-POBSERVEBUNDLE_bundle_latest_pobserve_window_for_chatgpt_upload_no_patch_no_order_20260603_103614.tar.gz
- run/evidence_bundles/A7-POBSERVEPRINT_bundle_latest_pobserve_window_for_chatgpt_upload_no_patch_no_order_20260603_103843.tar.gz
- run/evidence_bundles/A7-POBSERVEPRINT_bundle_latest_pobserve_window_for_chatgpt_upload_no_patch_no_order_20260603_112346.tar.gz

Expected recovery: about 30MB.

### Candidate B — old June-3 observe-window raw files

Only if Day-3 evidence already uploaded and no longer needed locally:

- run/live_capture/A7-REGULAR-OBSERVE-ONLY-WINDOW_background_env_correct_live_observation_latest_fetchable_no_patch_no_order_20min_20260603_102539/latest_decisions.raw
- run/live_capture/A7-REGULAR-OBSERVE-ONLY-WINDOW_background_env_correct_live_observation_latest_fetchable_no_patch_no_order_45min_20260603_103008/latest_decisions.raw

Expected recovery: about 236MB.

### Candidate C — old pseal directories before Day-4

Only after confirming Day-1/2/3 bundles are already uploaded or superseded:

- run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260601_154136
- run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260602_154342
- run/live_capture/B1-PROFIT-LIVE-R37F_DETACHED_PSEAL_FUNCTION_REPAIR_NO_ORDER_detached_market_close_seal_export_no_order_20260603_152920

Expected recovery: about 190MB+.

### Candidate D — old durable captures from June 1 / June 2

Potentially large, but only after you explicitly confirm they are not needed for replay/backtest or Day comparison:

- run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260601_100637
- run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260602_100035

Expected recovery: about 7.8G.

Important: these should not be deleted casually. They may be useful for comparing Day-4 to earlier days.

## Not recommended tonight

Do not delete:

- Day-4 durable capture, despite 4.3G size.
- replay/staging 6.2G decisions.jsonl from B3-R23 without replay-lane approval.
- run/proofs bulk directories.
- latest pdev_current bundle.
- any current source files or shell helper backups from today.

## Recommended cleanup route

1. Keep all Day-4 Lane X artifacts.
2. First delete only old small upload bundles and obvious duplicate raw fetch files if approved.
3. Next, ask separately before deleting June-1/June-2 durable captures.
4. Replay/staging cleanup should be handled in replay/disk lane, not Lane X.
