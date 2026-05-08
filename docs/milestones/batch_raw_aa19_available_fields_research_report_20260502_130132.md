# RAW-AA19 — Available Fields Research Report

generated_at_utc: 2026-05-02T07:31:32.175988+00:00
verdict: `RAW_AA19_AVAILABLE_FIELDS_RESEARCH_REPORT_READY`
blockers: `[]`

## Achieved

- Generated RAW research report using available fields only.
- Reported family/side/economics coverage.
- Reported observed net_pnl_after_costs only as observed source field.
- Preserved all gated and unavailable fields untouched.

## Safety

- No row mutation.
- No reward_cost_ratio derivation.
- No OI wall derivation.
- No PnL reconstruction.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Next

RAW_AA20_RESEARCH_REPORT_REVIEW_OR_AUTHORIZED_DECLARATION_INPUT
