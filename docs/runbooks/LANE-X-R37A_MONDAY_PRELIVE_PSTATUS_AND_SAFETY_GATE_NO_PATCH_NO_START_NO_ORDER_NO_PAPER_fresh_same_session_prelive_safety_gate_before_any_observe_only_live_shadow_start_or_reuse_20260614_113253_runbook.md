# Runbook — LANE-X-R37A_MONDAY_PRELIVE_PSTATUS_AND_SAFETY_GATE_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_fresh_same_session_prelive_safety_gate_before_any_observe_only_live_shadow_start_or_reuse_20260614_113253

This batch is pre-live only.

Allowed:
- bin/pstatus
- read-only Redis XLEN/TYPE/SCAN
- process snapshot
- dashboard read-only source/process scan
- git status short
- disk quick status
- write proof/report/milestone/runbook/handoff

Forbidden:
- broker order
- live trade
- paper trade
- risk service start
- execution service start
- replay start
- Redis delete/lock delete/stream delete
- threshold weakening

Proceed to R37B observe-only live-shadow start/reuse only if R37A classification is PASS.
