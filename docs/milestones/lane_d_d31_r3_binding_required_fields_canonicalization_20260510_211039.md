# LANE D D31-R3 — Binding Required Fields Canonicalization

Created: 2026-05-10T21:10:40+05:30

## Result

D31 binding-required field surface canonicalized.

## Cause

D31-R2 proved that BINDING_REQUIRED_FIELDS had length 16 because label safety fields were mixed into the replay-binding identity tuple.

## Repair

- Canonical replay-binding identity fields are frozen at 15.
- Label safety fields are separated into LABEL_SAFETY_FIELDS.
- Requirement rows now include:
  - 15 replay-binding fields
  - 2 label-safety rows
  - 1 D30 audit/status row
- binding_required_field_count remains 15.

## Safety

- No replay execution.
- No result-pack creation.
- No candidate context attachment.
- No candidate-trade matching.
- No label binding.
- No PnL calculation.
- No ML training/prediction.
- No broker calls.
- No live Redis writes.
- No paper/live enablement.
- No runtime service start.
- No strategy doctrine mutation.
- No replay engine mutation.
