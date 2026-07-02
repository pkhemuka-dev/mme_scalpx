# Runbook — LANE-X-R37A-R5_AFTERMARKET_FINAL_PREMONDAY_FREEZE_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_freeze_r37a_r2_r3_r4_aftermarket_safety_reseal_and_monday_fresh_gate_instruction_20260614_114052

Allowed now:
- read-only final freeze
- pstatus
- Redis scan/xlen only
- process snapshot
- git/disk status

Forbidden:
- patch
- start
- live-shadow start
- paper
- live
- broker order
- risk/execution/replay start
- Redis delete / lock delete / stream delete

Monday route:
1. Run fresh same-session R37A.
2. If PASS, run R37B observe-only live-shadow start/reuse.
3. Then run same-session verifier/watchers.
4. Controlled paper only after explicit user approval.
