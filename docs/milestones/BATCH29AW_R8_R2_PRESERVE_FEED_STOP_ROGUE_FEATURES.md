# Batch 29AW-R8-R2 — Preserve Feed, Stop Rogue Features

generated_at_utc: 2026-05-05T09:42:50.503309+00:00
verdict: `DEFER_29AW_R8_R2_PRESERVE_FEED_STOP_ROGUE_FEATURES`
provider_state: `NOT_FEED_READY`
readiness_verdict: `NOT_FEED_READY`
blockers: `['ZERODHA_MIN_ACTIVITY_OK_FALSE']`
warnings: `['FULL_PROVIDER_NOT_READY:NOT_FEED_READY', 'DHAN_LANES_INACTIVE_REQUIRES_SEPARATE_DHAN_LANE_DIAGNOSTIC']`

## Purpose
Stop rogue features/proof stack while preserving the live feed process and feed lock.

## Safety
- No production patch.
- No Redis restart.
- No feed restart.
- No strategy/risk/execution restart.
- No paper/live enablement.
- No order sending.

## Next
REPAIR_LISTED_29AW_R8_R2_BLOCKERS
