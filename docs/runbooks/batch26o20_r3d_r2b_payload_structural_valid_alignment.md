# Batch 26-O20-R3D-R2B — Returned Payload structural_valid Alignment

## Purpose

O20-R3D-R2A proved the persisted consumer-view surface and service samples were structurally valid, but failed only because the immediate `FeatureService.run_once` returned payload did not carry `consumer_view.structural_valid=true`.

R2B aligns the returned payload with the already-correct persisted Redis fields.

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

`PASS_O20_R3D_R2B_PAYLOAD_STRUCTURAL_VALID_ALIGNMENT_OK_HOLD_ONLY`

Then next:

`26-O20-R3E corrected bounded observation rerun after source-level validity repair`
