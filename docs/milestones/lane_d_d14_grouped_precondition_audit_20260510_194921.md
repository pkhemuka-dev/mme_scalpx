# LANE D D14 — Grouped Source-Map Precondition Audit

Created at: `2026-05-10T14:19:21.609234+00:00`

## Verdict

PASS — D14 grouped source-map precondition audit created and proved.

## Precondition Status

`BLOCKED_INCOMPLETE_REPLAY_GROUP`

## Scope

- Added `grouped_precondition_audit.py`.
- Added grouped source-map precondition config.
- Generated `17_grouped_source_map_precondition_audit.json`.
- Generated `09_optimizer_verdict.json`.

## Important Limitation

D14 is audit-only. Mixed replay roots are repaired, but the selected grouped source map is incomplete. No candidate-to-trade matching, label binding, PnL calculation, training, prediction, or optimization approval occurred.

## Safety

- No replay execution.
- No candidate-to-trade matching.
- No label binding.
- No real PnL calculation.
- No model training.
- No model prediction.
- No broker calls.
- No live Redis writes.
- No paper/live enablement.
- No runtime service start.
- No strategy doctrine mutation.
- No replay engine mutation.

## Next

LANE-D-D15: replay result pack discovery audit, no execution.
