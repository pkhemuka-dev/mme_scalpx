# R38DJ Patch Plan — Source Blocker Audit / No Restart / No Order

Tag: LANE-X-R38DJ_SOURCE_BLOCKER_AUDIT_PATCH_PREP_NO_RESTART_NO_ARM_NO_ORDER_20260617_121220
Created: 2026-06-17T12:12:33+05:30

## Safety status
- Redis orders/risk/execution/trades at start: 0/0/0/0
- No risk/execution process required before source patching.
- This run did not arm paper.
- This run did not start risk/execution.
- This run did not place broker/live/paper orders.
- This run did not issue Redis destructive commands.

## Today's live blocker summary
1. MISC CALL/PUT had fresh ZERODHA option and futures data, tradability passed, but failed at:
   - failed_stage: compression_detection
   - compression_missing_reason: compression_width_out_of_bounds
2. MISR had tradability/context but failed at:
   - failed_stage: active_trap_zone_selection
3. MISO remains excluded from controlled paper by current classic-only bridge unless separately proven.
4. Decision bridge is producing HOLD/no_candidate, not ENTER_CALL/ENTER_PUT.

## Patch principle
Do NOT force a trade.
Do NOT lower thresholds blindly in live.
First patch should improve deterministic eligibility diagnostics and threshold visibility:
- expose min/max compression width thresholds in MISC surfaces,
- expose exact active trap-zone selection blocker fields in MISR,
- expose bridge-side source fields so ENTER parser and decision bridge agree,
- keep paper fail-closed unless real ENTER_* appears.

## Files/lines to inspect
See: run/audits/LANE-X-R38DJ_SOURCE_BLOCKER_AUDIT_PATCH_PREP_NO_RESTART_NO_ARM_NO_ORDER_20260617_121220_source_hits.txt

## Next patch candidate
After reviewing source hits, create a guarded patch only if exact source location is confirmed:
- MISC: add threshold diagnostics + reason fields around compression width bounds; optionally allow config/env shadow tuning only, not candidate forcing.
- MISR: add active trap-zone diagnostic fields; no forced zone.
- Bridge: ensure branch/side is emitted for HOLD and candidate rows consistently.
- Watcher: parse nested candidate/action fields, not plain grep only.

