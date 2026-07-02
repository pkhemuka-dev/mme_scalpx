# Runbook — LANE-X-R37B_OBSERVE_ONLY_LIVESHADOW_START_OR_REUSE_NO_ORDER_NO_PAPER_start_or_reuse_monday_observe_only_live_shadow_after_r37a_pass_without_paper_live_risk_execution_replay_or_order_20260615_092101

Allowed:
- observe-only live-shadow start/reuse via approved helper pauto_start only
- pstatus
- Redis scan/type/xlen only
- process snapshot
- live_capture growth check

Forbidden:
- paper
- live trading
- broker order
- risk service start
- execution service start
- replay start
- Redis delete / lock delete / stream delete

If PASS, next is R37C/R34O fresh same-session live-shadow verifier.
