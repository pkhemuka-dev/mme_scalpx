# A6-FEED-R5T_read_only_execute_verified_pstackcheck_strategy_status_no_start_no_order_no_paper_20260515_100831

Batch: A6-FEED-R5T

Purpose: read_only_execute_verified_pstackcheck_strategy_status_no_start_no_order_no_paper

Final verdict: PASS_A6_FEED_R5T_PSTACKCHECK_STATUS_CAPTURED_NO_START_NO_ORDER_NO_PAPER

Safety: pstackcheck only after read-only definition verification; no pstack start, no service start/restart/stop, no patch, no restore, no clear/delete, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "decisions_present": true,
  "decisions_recent": false,
  "decisions_stream_age_ms": 948883,
  "decisions_stream_xlen": 1684,
  "features_recent": true,
  "features_stream_age_ms": 11184,
  "features_stream_xlen": 6,
  "likely_condition": "PSTACKCHECK_READ_ONLY_CAPTURED_STRATEGY_NOT_RUNNING_DECISIONS_STALE",
  "next_action": "Next requires explicit approval for observe-only strategy/features start or pstack helper start. No paper/live/risk/execution.",
  "pstackcheck_attempted": true,
  "pstackcheck_available": true,
  "pstackcheck_forbidden_markers": [],
  "pstackcheck_ok": true,
  "r5s_final_verdict": "PASS_A6_FEED_R5S_PSTACK_STRATEGY_START_GATE_INSPECTED_NO_START_NO_ORDER_NO_PAPER",
  "r5s_likely_condition": "READ_ONLY_PSTACKCHECK_AVAILABLE_STRATEGY_START_GATE_CAN_BE_CHECKED_BEFORE_APPROVED_START",
  "r5s_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5S_read_only_pstack_strategy_start_gate_inspection_after_stale_decisions_no_start_no_order_no_paper_20260515_100549.json",
  "standard_services_post": [],
  "standard_services_pre": []
}
```

pstackcheck result:

```json
{
  "attempted": true,
  "ok": true,
  "rc": 0,
  "stderr_redacted": "",
  "stdout_redacted": "===== PSTACKCHECK =====\n2026-05-15T10:08:37+05:30\n\n===== PROCESS STATUS =====\n--- feeds ---\nnot running\n--- features ---\nnot running\n--- strategy ---\nnot running\n--- execution ---\nnot running\n--- risk ---\nnot running\n--- monitor ---\nnot running\n--- report ---\nnot running\n\n===== REDIS SURFACE CHECK =====\nredis_ping = True\n\nSTREAM_TICKS_MME_FUT_ZERODHA           ticks:mme:fut:zerodha:stream                  xlen=148      growth_5s=2\nSTREAM_TICKS_MME_FUT_DHAN              ticks:mme:fut:dhan:stream                     xlen=40       growth_5s=0\nSTREAM_TICKS_MME_OPT_SELECTED_ZERODHA  ticks:mme:opt:selected:zerodha:stream         xlen=621      growth_5s=2\nSTREAM_TICKS_MME_OPT_SELECTED_DHAN     ticks:mme:opt:selected:dhan:stream            xlen=157      growth_5s=0\nSTREAM_TICKS_MME_OPT_CONTEXT_DHAN      ticks:mme:opt:context:dhan:stream             xlen=328      growth_5s=2\nSTREAM_FEATURES_MME                    features:mme:stream                           xlen=5        growth_5s=0\nSTREAM_DECISIONS_MME                   decisions:mme:stream                          xlen=1684     growth_5s=0\nSTREAM_SYSTEM_HEALTH                   system:health:stream                          xlen=6668     growth_5s=11\nSTREAM_SYSTEM_ERRORS                   system:errors:stream                          xlen=10009    growth_5s=-13\n\n===== LATEST FEATURE / DECISION SAMPLE KEYS =====\n\nSTREAM_FEATURES_MME = features:mme:stream\n  latest_id = 1778819915614-0\n  field_keys = ['consumer_view_json', 'family_features_json', 'family_features_version', 'family_surfaces_json', 'frame_id', 'frame_ts_ns', 'o23p_r6b_r3_family_payload_publish_patch', 'schema_version', 'service']\n\nSTREAM_DECISIONS_MME = decisions:mme:stream\n  latest_id = 1778818988600-0\n  field_keys = ['action', 'activation_action', 'activation_bridge_enabled', 'activation_candidate_count', 'activation_mode', 'activation_observed_action', 'activation_promoted', 'activation_reason', 'activation_report_json', 'activation_report_only', 'activation_safe_to_promote', 'activation_selected_action', 'activation_selected_branch_id', 'activation_selected_family_id', 'activation_selected_score', 'branch_id', 'confidence', 'consumer_view_json', 'data_valid', 'decision_id', 'diagnostics_json', 'doctrine_id', 'family_features_json', 'family_frames_json', 'family_scope_candidates_json', 'family_surfaces_json', 'features_generated_at_ns', 'hold_only', 'instrument_key', 'instrument_token', 'o23p_r10_decision_family_payload_patch', 'o23p_r13_decision_family_payload_patch', 'o23q_r13_family_scope_candidates_projection_patch', 'option_symbol', 'order_type', 'payload_json', 'price', 'provider_ready_classic', 'provider_ready_miso', 'qty']\n  action=HOLD\n  reason=hold_only_family_features_consumer_bridge\n  ts_event_ns=1778818988369058095\n  ts_ns=1778818988369058095\n\nSTREAM_SYSTEM_ERRORS = system:errors:stream\n  latest_id = 1778819922882-0\n  field_keys = ['detail', 'event_type', 'instance_id', 'service_name', 'ts_event_ns', 'ts_ns']\n  service_name=risk\n  instance_id=risk:mme-scalpx:1896\n  event_type=risk_pending_claim_error\n  detail=cmd:mme:stream:ResponseError:unknown command `XAUTOCLAIM`, with args beginning with: `cmd:mme:stream`, `cg:risk:mme:v1`, `risk:mme-scalpx:1896`, `10000`, `0-0`, `COUNT`, `10`, \n  ts_event_ns=1778819922586176939\n  ts_ns=1778819922586176939\n\n===== LOCKS =====\nKEY_LOCK_FEEDS           lock:feeds                     value=feeds:mme-scalpx:1896 ttl_ms=21345\nKEY_LOCK_STRATEGY        lock:strategy                  value=None ttl_ms=-2\nKEY_LOCK_EXECUTION       lock:execution                 value=execution:mme-scalpx:1896 ttl_ms=21600"
}
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "latest_r5s_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_pstack_start_executed": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible_post": true,
  "no_risk_execution_order_process_visible_pre": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent_post": true,
  "orders_mme_stream_zero_or_absent_pre": true,
  "position_flat_post": true,
  "position_flat_pre": true,
  "pstackcheck_attempted": true,
  "pstackcheck_available_now": true,
  "pstackcheck_definition_has_no_forbidden_markers": true,
  "r5s_found_read_only_pstackcheck_available": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5T_read_only_execute_verified_pstackcheck_strategy_status_no_start_no_order_no_paper_20260515_100831.json
