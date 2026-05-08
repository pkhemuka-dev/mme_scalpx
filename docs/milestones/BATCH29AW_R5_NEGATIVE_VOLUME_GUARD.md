# Batch 29AW-R5 — Negative Volume Guard + Feed Relock

generated_at_utc: 2026-05-05T09:19:10.345785+00:00
verdict: `DEFER_29AW_R5_NEGATIVE_VOLUME_GUARD_AND_FEED_RELOCK`
blockers: `['FEEDS_ALIVE_FALSE', 'FEEDS_LOCK_PRESENT_FALSE', 'FEEDS_LOCK_TTL_POSITIVE_FALSE', 'NEGATIVE_VOLUME_ERRORS_NOT_SEEN_AFTER_RESTART_FALSE', 'REQUIRED_TICK_STREAM_ACTIVITY_FALSE']`

## Purpose
Patch feeds normalizer so negative provider volume does not break FeedTick validation.

## Files changed
[
  "app/mme_scalpx/services/feeds.py"
]

## Safety
- Redis not restarted.
- Feeds restarted only.
- Features/strategy/risk/execution not restarted.
- No paper/live enablement.
- No order sending.

## Next
REPAIR_LISTED_29AW_R5_BLOCKERS
