# LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211

classification: **PASS**

## Important verdict
Read-only live-shadow verifier only. This does **not** authorize paper, live trading, broker order, risk service, execution service, or replay.

## Safety
- pstatus rc: `0`
- paper_route_allowed_norm: `false`
- paper_reason: ``
- orders/risk/execution streams: `0/0/0`
- risk/execution/replay procs: `0/0/0`

## Same-session capture
- latest_capture_dir: `run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740`
- fresh_dir_ok: `true`
- durable_size_delta: `24346379`

## Growth verifier
- growth_compare_rc: `0`
- fut_redis_grew: `true`
- opt_redis_grew: `true`
- features_redis_grew: `true`
- decisions_redis_grew: `true`
- durable_capture_grew: `true`

## Expected observe-only processes
- supervisor_present: `true`
- recorder_present: `true`
- features_process_present: `true`
- strategy_process_present: `true`

## Durable surface
```text
latest_dir=run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740
durable_dir=run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture

PRESENT 12K run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/fut_zerodha.jsonl.gz
PRESENT 48K run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/opt_selected_zerodha.jsonl.gz
PRESENT 7.5M run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/features.jsonl.gz
PRESENT 41M run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/decisions.jsonl.gz
PRESENT 24K run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/provider_runtime.jsonl.gz
PRESENT 8.9M run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/health.jsonl.gz
PRESENT 4.0K run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/errors.jsonl.gz
PRESENT 4.0K run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/state.json
PRESENT 4.0K run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture/heartbeat.json
```

## Growth comparison JSON
```json
{
  "stream_growth": {
    "decisions:mme:stream": {
      "type_t0": "stream",
      "type_t1": "stream",
      "xlen_t0": 271,
      "xlen_t1": 556,
      "xlen_delta": 285,
      "last_id_t0": "1781496132053-0",
      "last_id_t1": "1781496313652-0",
      "last_id_changed": true
    },
    "errors:mme:stream": {
      "type_t0": "none",
      "type_t1": "none",
      "xlen_t0": 0,
      "xlen_t1": 0,
      "xlen_delta": 0,
      "last_id_t0": "NONE",
      "last_id_t1": "NONE",
      "last_id_changed": false
    },
    "features:mme:stream": {
      "type_t0": "stream",
      "type_t1": "stream",
      "xlen_t0": 64,
      "xlen_t1": 133,
      "xlen_delta": 69,
      "last_id_t0": "1781496131259-0",
      "last_id_t1": "1781496313575-0",
      "last_id_changed": true
    },
    "health:mme:stream": {
      "type_t0": "none",
      "type_t1": "none",
      "xlen_t0": 0,
      "xlen_t1": 0,
      "xlen_delta": 0,
      "last_id_t0": "NONE",
      "last_id_t1": "NONE",
      "last_id_changed": false
    },
    "provider_runtime:mme:stream": {
      "type_t0": "none",
      "type_t1": "none",
      "xlen_t0": 0,
      "xlen_t1": 0,
      "xlen_delta": 0,
      "last_id_t0": "NONE",
      "last_id_t1": "NONE",
      "last_id_changed": false
    },
    "ticks:mme:fut:zerodha:stream": {
      "type_t0": "stream",
      "type_t1": "stream",
      "xlen_t0": 317,
      "xlen_t1": 351,
      "xlen_delta": 34,
      "last_id_t0": "1781496132060-0",
      "last_id_t1": "1781496308730-0",
      "last_id_changed": true
    },
    "ticks:mme:opt:selected:zerodha:stream": {
      "type_t0": "stream",
      "type_t1": "stream",
      "xlen_t0": 1597,
      "xlen_t1": 1789,
      "xlen_delta": 192,
      "last_id_t0": "1781496131749-0",
      "last_id_t1": "1781496313518-0",
      "last_id_changed": true
    }
  },
  "capture_size_t0": 35078360,
  "capture_size_t1": 59374442,
  "capture_size_delta": 24296082,
  "durable_size_t0": 35042307,
  "durable_size_t1": 59388686,
  "durable_size_delta": 24346379,
  "fut_redis_grew": true,
  "opt_redis_grew": true,
  "features_redis_grew": true,
  "decisions_redis_grew": true,
  "provider_runtime_redis_grew": false,
  "health_redis_grew": false,
  "durable_capture_grew": true
}
```

## Provider runtime tail
```json
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496301583307067"},"id":"1781496301619-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496302390214309"},"id":"1781496302600-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496303192349713"},"id":"1781496303227-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496303566367727"},"id":"1781496303679-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496304202598555"},"id":"1781496304244-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496304930781868"},"id":"1781496304977-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496305661235776"},"id":"1781496305720-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496306013410643"},"id":"1781496306103-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496306365657210"},"id":"1781496306378-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496306588967153"},"id":"1781496306933-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496307383187729"},"id":"1781496307590-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496307920381667"},"id":"1781496308072-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496308639836604"},"id":"1781496308988-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496309456920723"},"id":"1781496309495-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496310172274656"},"id":"1781496310367-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496310571338209"},"id":"1781496310600-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496310794014645"},"id":"1781496310920-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496311381127143"},"id":"1781496311445-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496312042827337"},"id":"1781496312076-0","stream":"provider:runtime:stream"}
{"fields":{"blocked_reason":"","failover_mode":"MANUAL","family_runtime_mode":"OBSERVE_ONLY","from_provider_id":"ZERODHA","has_open_position":"","message":"","new_status":"HEALTHY","override_mode":"AUTO","previous_status":"FAILOVER_ACTIVE","reason":"BOOTSTRAP","role":"selected_option_marketdata","setup_invalidated":"False","switch_allowed":"True","to_provider_id":"ZERODHA","ts_event_ns":"1781496312540981894"},"id":"1781496312652-0","stream":"provider:runtime:stream"}
```

## Heartbeat
```json
{
  "counts": {
    "decisions": 704,
    "errors": 2,
    "features": 167,
    "fut_zerodha": 91,
    "health": 1425,
    "opt_selected_zerodha": 434,
    "provider_runtime": 778
  },
  "heartbeat_at_utc": "2026-06-15T04:05:12.077679+00:00",
  "last_ids": {
    "decisions:mme:stream": "1781496311400-0",
    "features:mme:stream": "1781496310421-0",
    "provider:runtime:stream": "1781496312076-0",
    "system:errors:stream": "1781495956575-0",
    "system:health:stream": "1781496311449-0",
    "ticks:mme:fut:zerodha:stream": "1781496308730-0",
    "ticks:mme:opt:selected:zerodha:stream": "1781496311382-0"
  },
  "outdir": "run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture",
  "pid": 2406,
  "read_only": true,
  "redis_xlens": {
    "decisions": 553,
    "errors": 10018,
    "features": 132,
    "fut_zerodha": 351,
    "health": 10033,
    "opt_selected_zerodha": 1787,
    "provider_runtime": 6250
  },
  "running": true,
  "safety": {
    "execution_xlen": 0,
    "orders_xlen": 0,
    "risk_xlen": 0
  },
  "service": "b1_profit_live_durable_capture"
}```

## State
```json
{
  "counts": {
    "decisions": 704,
    "errors": 2,
    "features": 167,
    "fut_zerodha": 91,
    "health": 1425,
    "opt_selected_zerodha": 434,
    "provider_runtime": 778
  },
  "last_ids": {
    "decisions:mme:stream": "1781496311400-0",
    "features:mme:stream": "1781496310421-0",
    "provider:runtime:stream": "1781496312076-0",
    "system:errors:stream": "1781495956575-0",
    "system:health:stream": "1781496311449-0",
    "ticks:mme:fut:zerodha:stream": "1781496308730-0",
    "ticks:mme:opt:selected:zerodha:stream": "1781496311382-0"
  },
  "safety": {
    "execution_xlen": 0,
    "orders_xlen": 0,
    "risk_xlen": 0
  },
  "updated_at_utc": "2026-06-15T04:05:12.080571+00:00"
}```

## Project processes
```text
   2267    1254 S          07:34 .venv/bin/python bin/b1_profit_live_capture_supervisor.py --outdir run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740 --action-mode apply --interval-sec 15 --stale-after-ms 30000
   2406    2267 Ss         07:33 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python /home/Lenovo/scalpx/projects/mme_scalpx/bin/b1_profit_live_durable_capture.py --outdir run/live_capture/B1-PROFIT-LIVE-R37C_CAPTURE_SUPERVISOR_APPLY_20260615_092740/durable_capture --no-backfill
   2437    2267 Ss         07:33 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --skip-group-bootstrap
   2438    2267 Rs         07:33 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --skip-group-bootstrap
   4205       1 Ssl        05:48 /home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main
```

## Reasons
same-session observe-only live-shadow verified: fut/opt/features/decisions growth plus fresh durable capture and expected observe-only processes

## Artifact paths
- proof path: `run/proofs/LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211.json`
- report path: `run/audits/LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211_report.md`
- milestone path: `docs/milestones/LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211.md`
- runbook path: `docs/runbooks/LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211_runbook.md`
- handoff path: `run/handoffs/LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211_handoff.md`
- raw dir: `run/audits/LANE-X-R37C_R34O_FRESH_SAME_SESSION_LIVESHADOW_VERIFIER_NO_ORDER_NO_PAPER_verify_monday_same_session_observe_only_live_shadow_after_r37b_r2_growth_pass_without_start_stop_patch_order_paper_20260615_093211_raw`

## Next recommended batch
`LANE-X-R37D_LIVE_SHADOW_CANDIDATE_AND_BLOCKER_WATCH_NO_ORDER_NO_PAPER`
