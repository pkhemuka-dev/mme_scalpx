# LANE-X-R38CS_CANDIDATE_METADATA_CONTRACT_REPAIR_PREFLIGHT_NO_ARM_NO_ORDER_20260616_144920 metadata contract repair plan

## Current blocker

R38CR blocked final pre-arm because latest MISB PUT candidate is missing:

- quantity_lots_hint
- entry_mode

## Allowed repair scope

Allowed:
- Fill candidate metadata contract only.
- Set paper/prearm lot intent explicitly to 1 lot for the controlled-paper scope.
- Set entry_mode to a non-live controlled-paper/preflight-safe mode string.
- Preserve option_symbol, instrument_token, option_price, target_points, stop_points, tick_size.
- Keep observe-only.
- Keep activation dry_run/report_only until separate final scope ack.

Forbidden:
- No paper arm.
- No live order.
- No risk/execution start.
- No Redis delete/trim.
- No threshold relaxation.
- No all-strategy paper.

## Intended controlled-paper scope after repair

family=MISB
side=PUT
action=ENTER_PUT
paper_lots=1
max_paper_events=1
mode=CONTROLLED_PAPER_ONLY
