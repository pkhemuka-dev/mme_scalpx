# Batch 29BA — Compact Payload Hardening Runbook

generated_at_utc: 2026-05-05T07:39:31.526329+00:00

## Current safe operating mode

- Keep feeds-only running.
- Keep features stopped.
- Keep strategy stopped.
- Do not restart full stack until compact payload hardening is complete.

## Diagnosis

- Features/strategy hot Redis writers likely caused Redis pressure.
- Feeds-only mode recovered tick stream growth and kept orders stream zero.

## Patch policy

- Patch only after full publisher/consumer source inspection.
- Compact hot Redis payloads first.
- Preserve heavy diagnostics outside hot Redis.
- Do not change doctrine, order flow, risk/execution behavior, or stream names.

## Candidate next batches

1. 29BB — compact features/decisions payload patch if exact seam is proven.
2. 29BB-ALT — redisx/settings maxlen/timeout patch if transport authority is proven.
3. 29AQ-R2-FEEDS-ONLY — feed-only readiness if market window still matters.
