# Monday live-shadow observe-only rehearsal runbook

Classification target: PASS_R34N_READY_FOR_MONDAY_LIVE_SHADOW_REHEARSAL_NOT_FINAL_PAPER_GATE

## Scope
Lane X only. Observe-only live-shadow rehearsal first. This is NOT final paper arming.

## Hard safety
- Do not set SCALPX_ENABLE_LIVE.
- Do not set SCALPX_ENABLE_PAPER.
- Do not set SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME.
- Do not start risk service.
- Do not start execution service.
- Do not delete Redis streams or locks.
- Broker/order path must remain blocked.

## Current readiness
- R34F candidate truth export: patched.
- R34K symbol/token identity helper: patched.
- R34M exact runtime identity source: patched.
- R34M-R1 synthetic smoke: PASS.
- R34N readiness freeze: PASS.
- Old Friday durable had candidate rows but identity_rows=0; old durable cannot prove identity.
- Monday fresh live-shadow must prove candidate truth rows include symbol/token.

## Monday target proof
Fresh live-shadow candidate truth must show:
- candidate_true_shadow > 0
- candidate_id/family/branch/side/score present
- symbol or instrument_token present
- top-level action remains HOLD
- payload_json.action remains HOLD
- broker_calls_executed_shadow = 0
- real_order_sent_shadow = 0
- redis_trading_stream_write_attempted_shadow = 0
- orders/risk/execution streams remain 0 before paper gate
