# Batch 26-O20-R3D-R2 — Source-Level Consumer-View Publish Repair

## Purpose

O20-R3D and O20-R3D-R1 failed because wrappers/markers were present but persisted `consumer_view_json` still remained invalid.

R2 stops adding wrappers and instead patches the actual source publish surface inside `features.py` where `consumer_view_json` and `payload_json` are serialized.

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
- Strategy must remain HOLD if no eligible branch exists.

## Required PASS

`PASS_O20_R3D_R2_SOURCE_PUBLISH_REPAIR_OK_HOLD_ONLY`

Then next:

`26-O20-R3E corrected bounded observation rerun after source-level validity repair`
