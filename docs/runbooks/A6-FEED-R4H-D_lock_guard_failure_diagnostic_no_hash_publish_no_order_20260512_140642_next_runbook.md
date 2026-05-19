# A6-FEED-R4H-D next runbook

## Status

`PASS_A6_FEED_R4H_D_LOCK_GUARD_FAILURE_CLASSIFIED_NO_HASH_PUBLISH_NO_ORDER`

## Root cause

`R4H_LOCK_GUARD_TRANSIENT_FAILURE_NOW_STABLE`

## Next

`A6-FEED-R4H-R2 direct-health guarded canonical hash publish retry / requires same approval`

## Rule

Do not publish hashes until lock guard behavior is resolved and all direct health guards remain true.
A6-PAPER remains blocked until A6-FEED-R5 passes.
