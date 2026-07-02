# Monday cockpit: live-shadow to controlled-paper ladder

## Current position

We are ready for Monday observe-only live-shadow.

We are not yet cleared for final controlled paper until R34O fresh live data proves:

- candidate_true_shadow > 0
- candidate_symbol_shadow or candidate_instrument_token_shadow present
- top-level action remains HOLD
- payload_json.action remains HOLD/blank
- orders/risk/execution remain 0

## Hard safety rules

Do not set these before R34O PASS:

- SCALPX_ENABLE_LIVE
- SCALPX_ENABLE_PAPER
- SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME
- SCALPX_CONTROLLED_PAPER_SCOPE_ACK

Do not start:

- risk service
- execution service

Do not delete:

- Redis streams
- locks
- live capture
- replay data

## Monday timeline

### 09:00–09:10 IST: premarket safety

Goal: confirm no accidental order/risk/execution path is active.

Required pass:

- orders:mme:stream = 0
- risk:mme:stream = 0
- execution:mme:stream = 0
- no risk/execution process
- compile ok
- disk ok

### 09:10–09:20 IST: observe-only stack start/reuse

Goal: start/reuse observe-only capture/strategy only.

Allowed:

- feeds
- features
- strategy
- dashboard/observer
- live capture

Not allowed:

- paper
- live
- risk
- execution
- broker order path

### 09:20–10:00 IST: R34O live-shadow watch

Goal: wait for first real fresh candidate-truth row.

Pass condition:

- candidate_true_shadow > 0
- candidate_action_shadow is ENTER_CALL or ENTER_PUT
- candidate_family_id_shadow present
- candidate_branch_id_shadow present
- candidate_score_shadow present
- candidate_symbol_shadow or candidate_instrument_token_shadow present
- top-level action HOLD
- payload_json.action HOLD/blank
- broker_calls_executed_shadow = 0
- real_order_sent_shadow = 0
- redis_trading_stream_write_attempted_shadow = 0

### If R34O PASS

Then and only then prepare a separate controlled-paper arming micro-batch.

Controlled paper must still be tiny:

- one strategy family only
- one symbol/instrument only
- one candidate only
- qty minimal/paper-only
- flatten/kill switch checked first
- broker/live cash hard blocked

### If candidate appears but identity missing

Do not paper-arm.

Run identity-focused live audit:

- inspect selected_option
- inspect view.common selected_call/selected_put
- inspect provider_runtime
- inspect Zerodha selected option snapshot
- inspect Dhan context state

### If no candidate by 10:30

Do not patch blindly.

Run candidate blocker watcher:

- family scores
- failed_stage
- provider_ready_classic
- option_tradability_pass
- futures_impulse
- selected option identity
- runtime mode

### If no candidate by 11:30

Still do not force trade.

Decide whether MIV-R research shadow is useful only as audit pressure, not paper strategy.

### If R34O never passes

No controlled paper that day.

Freeze day, collect evidence, patch exact blocker after market.

## What success means Monday

Success is not “any trade”.

Success is:

1. A real candidate appears.
2. It has symbol/token.
3. System still keeps HOLD until explicitly armed.
4. Then controlled-paper can be armed safely in a separate micro-batch.


## Seal
- classification: PASS_R34W_MONDAY_COCKPIT_PLAN_READY_NO_PATCH_NO_REPLAY_NO_ORDER
- proof: `run/proofs/LANE-X-R34W_MONDAY_LIVE_SHADOW_TO_CONTROLLED_PAPER_COCKPIT_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_write_exact_monday_go_nogo_ladder_for_r34o_live_shadow_then_controlled_paper_only_if_identity_and_safety_gate_pass_20260613_145703.json`
- compile_rc: 0
- orders/risk/execution: 0 / 0 / 0
- risk/execution proc: 0 / 0
- R34F/R34K/R34M markers: 2 / 2 / 2

## Disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       155G   95G   61G  61% /

## Strategy markers
433:# R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_BEGIN
448:    # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_BEGIN
502:    candidate_symbol_shadow = _safe_str(
505:    candidate_instrument_token_shadow = _safe_str(
508:    # R34K_SYMBOL_TOKEN_IDENTITY_EXPORT_END
525:        "candidate_symbol_shadow": candidate_symbol_shadow if is_enter else "",
526:        "candidate_instrument_token_shadow": candidate_instrument_token_shadow if is_enter else "",
527:        "symbol": candidate_symbol_shadow if is_enter else "",
528:        "instrument_token": candidate_instrument_token_shadow if is_enter else "",
533:# R34F_SHADOW_CANDIDATE_TRUTH_EXPORT_END
1087:        # R34M_EXACT_RUNTIME_IDENTITY_SOURCE_BEGIN
1094:        # R34M_EXACT_RUNTIME_IDENTITY_SOURCE_END
