# Batch 29AW-R6 — All FeedTick Volume Guard + Feed Relock

generated_at_utc: 2026-05-05T09:22:15.302679+00:00
verdict: `DEFER_29AW_R6_ALL_FEEDTICK_VOLUME_GUARD_AND_FEED_RELOCK`
blockers: `['FEEDS_ALIVE_FALSE', 'FEEDS_LOCK_PRESENT_FALSE', 'FEEDS_LOCK_TTL_POSITIVE_FALSE', 'NEGATIVE_VOLUME_ERRORS_NOT_SEEN_AFTER_BACKGROUND_START_FALSE', 'REQUIRED_TICK_STREAM_ACTIVITY_FALSE']`

## Purpose
Guard all FeedTick volume call sites and prove current foreground feeds no longer fail on negative volume.

## Files changed
[
  "app/mme_scalpx/services/feeds.py"
]

## Safety
- Redis not restarted.
- Feeds only restarted after foreground smoke if safe.
- Features/strategy/risk/execution not restarted.
- No paper/live enablement.
- No order sending.

## Next
REPAIR_LISTED_29AW_R6_BLOCKERS
