# Batch 29BD-R2 — Clean Full Provider Feeds Capture

generated_at_utc: 2026-05-05T09:51:41.841782+00:00
verdict: `DEFER_29BD_R2_CLEAN_FULL_PROVIDER_FEEDS_CAPTURE`
blockers: `['FEATURES_INACTIVE_CAPTURE_FALSE', 'DECISIONS_INACTIVE_CAPTURE_FALSE']`
warnings: `[]`

## Purpose
Pre-clean old proof/features contamination and capture full-provider feeds-only evidence.

## Key facts
- Capture JSON: `run/live_recovery/batch29bd_r2_clean_full_provider_feeds_capture_20260505_152141/capture/clean_full_provider_feeds_capture_29bd_r2.json`
- Capture CSV: `run/live_recovery/batch29bd_r2_clean_full_provider_feeds_capture_20260505_152141/capture/clean_full_provider_feeds_capture_29bd_r2.csv`
- Archive: `run/live_recovery/batch29bd_r2_clean_full_provider_feeds_capture_20260505_152141/batch29bd_r2_clean_full_provider_feeds_capture_20260505_152141.tar.gz`
- Archive SHA256: `7ed7564c5537237b20707551b1bd3677b855840300ff85b25612ece47c2fffbe`

## Safety
- No production patch.
- No Redis restart.
- No feed restart.
- Features/strategy/risk/execution remained stopped.
- No paper/live enablement.
- No order sending.

## Next
REPAIR_LISTED_29BD_R2_BLOCKERS
