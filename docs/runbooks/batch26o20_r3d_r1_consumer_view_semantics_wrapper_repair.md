# Batch 26-O20-R3D-R1 — Consumer-View Semantics Wrapper Repair

## Purpose

O20-R3D applied a consumer-view semantics guard, but proof showed persisted Redis values still had:

- `consumer_view_json.data_valid=false`
- `consumer_view_json.safe_to_consume=false`
- `consumer_view_json.structural_valid=null`

R1 repairs the failed wrapper stacking by wrapping `FeatureService.run_once` directly and correcting the final persisted `HASH_FEATURES` values after the original publish.

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

## Doctrine Boundary

- `data_valid=True` means structurally safe for strategy consumption.
- Branch `eligible` and `tradability_ok` remain doctrine truth.
- No branch is promoted.
- No candidate is forced.
- Strategy must remain HOLD when no eligible branch exists.

## Required PASS

`PASS_O20_R3D_R1_CONSUMER_VIEW_SEMANTICS_WRAPPER_REPAIR_OK_HOLD_ONLY`

Then next:

`26-O20-R3E corrected bounded observation rerun after validity semantics repair`
