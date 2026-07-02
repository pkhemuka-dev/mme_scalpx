# Runbook — LANE-X-R37A-MONDAY-FRESH_PRELIVE_PSTATUS_AND_SAFETY_GATE_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_fresh_monday_same_session_prelive_safety_gate_before_any_observe_only_live_shadow_start_or_reuse_20260615_091733

Allowed:
- pstatus
- read-only Redis scan/type/xlen
- process snapshot
- dashboard callable danger scan
- source truth file check
- git/disk status

Forbidden:
- patch
- start/reuse live-shadow
- paper
- live
- broker order
- risk service start
- execution service start
- replay start
- Redis delete / lock delete / stream delete

If PASS, next batch is R37B observe-only live-shadow start/reuse.
