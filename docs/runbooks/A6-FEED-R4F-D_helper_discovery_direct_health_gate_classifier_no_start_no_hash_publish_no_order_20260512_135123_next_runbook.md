# A6-FEED-R4F-D next runbook

## Status

`PASS_A6_FEED_R4F_D_HELPER_DISCOVERY_DIRECT_HEALTH_CLASSIFIED_NO_START_NO_HASH_PUBLISH_NO_ORDER`

## Root cause

`HELPER_DISCOVERY_MISSING_BUT_DIRECT_FEED_HEALTH_OK`

## Next

`A6-FEED-R4G direct-health guarded canonical hash publish plan / no hash publish until approved`

## Rule

If direct feed health is OK but pfeed helpers are unavailable, use a direct-health guarded hash publish plan before any hash write.
No paper branch until canonical hashes and feature/decision readiness pass.
