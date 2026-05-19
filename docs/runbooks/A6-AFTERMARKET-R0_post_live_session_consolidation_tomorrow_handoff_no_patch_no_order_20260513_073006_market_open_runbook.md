# A6-AFTERMARKET-R0 — Market-open continuation runbook

## Current status

`A6_FEED_R5_L_OUTPUT_MISSING`

## Paper status

`A6_PAPER_STILL_BLOCKED_UNTIL_A6_FEED_R5_READINESS_PASS`

## First action at market open

`Paste/run A6-FEED-R5-L result first; then continue based on verdict`

## Absolute safety rules

- No real live.
- No broker order until fresh controlled-paper approval.
- No risk/execution start until A6-PAPER explicitly reaches that stage.
- No all-5 simultaneous paper firing.
- One selected scoped signal only.
- 1 lot only.
- Paper/sandbox only.
- No broker failover.
- No mid-position provider migration.
- Stop if orders:mme:stream is not 0.
- Stop if state:position:mme is not FLAT.
- Stop if provider/feed hashes are not ready/fresh/current.
- Stop if feature/decision consumers still show provider_not_ready/view_data_invalid.

## Next likely sequence

1. Complete/paste `A6-FEED-R5-L` result if not already done.
2. If `A6-FEED-R5-L` PASS: run `A6-FEED-R5-R2`.
3. If `A6-FEED-R5-R2` PASS: resume `A6-PAPER` watcher/preflight.
4. Only then ask for a fresh exact one-scope controlled-paper approval phrase.
