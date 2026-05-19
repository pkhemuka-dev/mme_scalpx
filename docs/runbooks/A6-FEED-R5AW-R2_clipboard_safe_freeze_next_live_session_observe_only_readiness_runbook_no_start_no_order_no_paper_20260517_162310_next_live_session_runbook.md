# A6-FEED-R5AW-R2_clipboard_safe_freeze_next_live_session_observe_only_readiness_runbook_no_start_no_order_no_paper_20260517_162310 — Next Live Session Runbook

## Current closure

A6-FEED-R5AV after-market static closure is the prerequisite.

Latest R5AV proof:

/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AV_broader_aftermarket_static_closure_after_r5au_contract_payload_pass_no_patch_no_restart_no_order_no_paper_20260517_162027.json

## Current state at runbook creation

{
  "orders_mme_stream_xlen": 0,
  "position_flat": true,
  "services": []
}

## Allowed next live market session only

- Observe-only feeds/features/strategy start or restart, only after explicit approval.
- No risk service.
- No execution service.
- No paper mode.
- No live mode.
- No broker orders.
- orders:mme:stream must remain 0.
- position must remain FLAT.

## Exact approval required before live-session command

I APPROVE A6-FEED LIVE-SESSION OBSERVE-ONLY READINESS CHECK: START/RESTART FEEDS, FEATURES, STRATEGY ONLY IF NEEDED, NO PAPER, NO LIVE, NO BROKER ORDER, NO RISK/EXECUTION START, ORDERS STREAM MUST REMAIN 0, POSITION MUST REMAIN FLAT

## Live-session proof goals

1. Provider/feed streams current and growing.
2. Dhan option context current and growing.
3. features:mme:stream current and growing.
4. decisions:mme:stream current and growing.
5. orders:mme:stream remains 0.
6. position remains FLAT.
7. no risk/execution process visible.
8. no paper/live/broker flags enabled.

## Stop condition

If all pass, A6-FEED can move toward readiness PASS.
If any fail, remain blocked and inspect read-only logs/proofs only.
