# Batch 26-O17 — Activation Candidate Extraction Proof

## Purpose

O17 proves that after O16H-R2:

- feature frame is valid,
- `consumer_view_json` is present,
- `consumer_view.data_valid = true`,
- `consumer_view.safe_to_consume = true`,
- all 10 branch frames are present,
- `mist_call` branch frame is visible to activation,
- activation can honestly proceed to candidate extraction or doctrine-based skip.

## Safety

This batch does not:

- start paper,
- start risk,
- start execution,
- call broker,
- write orders,
- approve real live,
- force candidates,
- relax thresholds.

## Required PASS

`PASS_O17_ACTIVATION_VIEW_CANDIDATE_EXTRACTION_READY_NO_ORDER`

Then next batch:

- `26-O18 lightweight controlled-paper preflight`
- MIST CALL only
- 1 lot only
- no heavy O11 monitor
- real-live false

If O17 returns one-shot interface review, do O17A first.
