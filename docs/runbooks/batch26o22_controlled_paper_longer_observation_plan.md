# Batch 26-O22 — Controlled-Paper Longer Observation Plan / Runbook

## Purpose

O22 is plan/runbook only. It does not start paper runtime.

It confirms that the evidence chain is ready for the next controlled-paper-only longer observation phase.

## Evidence Chain Required

- O18 lightweight controlled-paper preflight PASS
- O19 lightweight controlled-paper runtime PASS
- O20R recovery PASS
- O20-R2 bounded short observation PASS
- O21 promotion readiness review PASS with real-live blocked
- O21R post-O21 orphan cleanup PASS

## Safety Boundary

O22 does not:

- start paper,
- start risk,
- start execution,
- call broker,
- write orders,
- enable real live,
- force candidates,
- relax thresholds.

## Current Required State

- Orders stream length remains zero.
- Position hash remains FLAT.
- Real-live remains false.
- Latest decisions are HOLD-only.
- features/strategy/risk/execution are not running after cleanup.
- Feeds may be started later by O23 only if required.

## O23 Proposed Scope

- Controlled paper only.
- MIST CALL only.
- 1 lot only.
- Real-live false.
- No automatic broker failover.
- No mid-position provider migration.
- No heavy O11 monitor.
- No unbounded Redis polling.
- Bounded samples only.
- Fail-safe proof writing on interruption.
- Cleanup of started services at exit.

## O23 Proposed Runtime

Default:

- `BATCH26O23_RUN_SECONDS=900`
- `BATCH26O23_SAMPLE_COUNT=18`

Bounds:

- minimum 600 seconds
- maximum 1800 seconds
- sample count 10 to 30

## O23 PASS Conditions

- O22 PASS gate.
- Compile/import pass.
- Position FLAT before/during/after.
- Real-live false before/during/after.
- Orders remain zero.
- Latest orders empty.
- Decisions stream grows.
- Features stream grows.
- Decisions remain HOLD-only unless report-only candidate appears.
- Any report-only candidate must stay non-promoted, no broker side effects, no live order flags.
- Risk/execution/strategy/features run in most samples.
- No threshold relaxation.
- No forced candidate.
- No heavy monitor.
- No unbounded polling.
- All started services cleaned at exit.

## Promotion Policy After O23

If O23 sees no candidate, continue longer paper or wait for better market structure. Do not force a candidate.

If O23 sees a report-only candidate, audit candidate lineage, risk veto, and execution route preview before any broker-order path.

If any order appears or position opens unexpectedly, fail immediately and reconcile.

Real live remains blocked after O23.
