# Negative volume feed normalizer fix — 20260505_150312

## Problem
Live feed loop produced repeated FeedTick model validation errors:
volume must be >= 0, got large negative provider values.

## Fix
Kept core FeedTick model strict.
Added feed-normalizer guard to clamp negative provider volume to 0 before model construction.
Logs/counts anomaly as provider normalization issue.

## Safety
- No execution service started.
- No risk/execution patch.
- No model relaxation.
- Fix remains in feed normalization layer.

## Proofs
- run/proofs/fix_negative_volume_feed_normalizer_20260505_150312_feeds_surface_refs.txt
- run/proofs/fix_negative_volume_feed_normalizer_20260505_150312_compile.txt
- run/proofs/fix_negative_volume_feed_normalizer_20260505_150312_static_proof.txt
