# Batch 26-O20-R3D — Consumer-View Validity Semantics Repair

## Purpose

O20-R3C proved ABI was clean but consumer-view `data_valid=false` because runtime market-data/tradability was blocked/degraded.

O20-R3D separates two meanings:

1. **Consumer-view structural validity**: strategy can safely consume the frame.
2. **Doctrine/trade eligibility**: branch-level `eligible` / `tradability_ok` decides whether any setup can be promoted.

This batch sets consumer-view valid only when the 10-branch frame is structurally complete and ABI-clean. It does not mark any branch eligible, does not force a candidate, and does not relax thresholds.

## Safety

This batch does not:

- start paper,
- start risk,
- start execution,
- call broker,
- write orders,
- enable real live,
- relax thresholds,
- force candidates.

## Required PASS

`PASS_O20_R3D_CONSUMER_VIEW_VALIDITY_SEMANTICS_OK_HOLD_ONLY`

Then next:

`26-O20-R3E corrected bounded observation rerun after validity semantics repair`
