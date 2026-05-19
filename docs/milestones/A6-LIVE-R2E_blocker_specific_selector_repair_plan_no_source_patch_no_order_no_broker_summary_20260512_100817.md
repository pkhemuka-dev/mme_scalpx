# A6-LIVE-R2E — Blocker-specific selector repair plan

Generated IST: `2026-05-12T10:08:17.245859+05:30`

## Verdict

`PASS_A6_LIVE_R2E_BLOCKER_SPECIFIC_PLAN_READY_NO_SOURCE_PATCH_NO_ORDER_NO_BROKER`

## Blocker class

`HOLD_ONLY_MODE_ACTIVE`

## Plan decision

`CONFIG_OR_ACTIVATION_GATE_PLAN_REQUIRED_NO_SOURCE_PATCH_YET`

## Key counts

- reason_counts: `{'hold_only_family_features_consumer_bridge': 80}`
- activation_reason_counts: `{'no_candidate': 66, 'view_data_invalid': 14}`
- action_counts: `{'HOLD': 160}`
- readiness_true_counts: `{'activation_report_only': 80, 'activation_bridge_enabled': 80, 'provider_ready_classic': 66, 'data_valid': 66, 'warmup_complete': 80, 'safe_to_consume': 80, 'hold_only': 80, 'candidate.safe_to_consume': 160, 'candidate.data_valid': 198, 'candidate.provider_ready_classic': 438, 'candidate.provider_ready_miso': 240, 'candidate.session_eligible': 80, 'candidate.freshness_ok': 80, 'candidate.valid': 14756, 'candidate.fresh': 15746, 'candidate.is_active_provider_snapshot': 2800, 'candidate.active_valid': 80, 'candidate.dhan_valid': 80, 'candidate.providers_aligned': 80, 'candidate.cross_option_ready': 7280, 'candidate.chain_context_ready': 3680, 'candidate.oi_wall_ready': 17680, 'candidate.provider_ready': 6480, 'candidate.liquidity_pass': 80, 'candidate.spread_pass': 7040, 'candidate.depth_pass': 7040, 'candidate.impact_pass': 7040, 'candidate.stale_pass': 7040, 'candidate.crossed_book_pass': 7040, 'candidate.queue_pass': 7040, 'candidate.futures_liquidity_pass': 1760, 'candidate.entry_pass': 2024, 'candidate.context_pass': 2560, 'candidate.fallback_ready': 2560, 'candidate.option_tradability_pass': 800, 'candidate.tradability_pass': 800}`
- readiness_false_counts: `{'activation_safe_to_promote': 80, 'activation_promoted': 80, 'provider_ready_miso': 80, 'provider_ready_classic': 14, 'data_valid': 14, 'candidate.safe_to_promote': 160, 'candidate.eligible': 6020, 'candidate.activation_safe_to_promote': 80, 'candidate.provider_ready_miso': 240, 'candidate.provider_runtime_mode': 240, 'candidate.provider_runtime_blocked': 240, 'candidate.provider_runtime_block_reason': 240, 'candidate.dhan_context_fresh': 80, 'candidate.contract_eligible': 400, 'candidate.surface_eligible': 400, 'candidate.valid': 80, 'candidate.is_active_provider_snapshot': 880, 'candidate.depth20_ready': 960, 'candidate.response_pass': 5280, 'candidate.entry_pass': 5016, 'candidate.provider_exchange_segment': 80, 'candidate.oi_wall_ready': 80, 'candidate.fresh': 80, 'candidate.miso_context_ready': 80, 'candidate.call_ready': 400, 'candidate.put_ready': 400, 'candidate.dominant_ready_branch': 400, 'candidate.branch_ready': 3360, 'candidate.resume_override_pass': 640, 'candidate.option_tradability_pass': 2560, 'candidate.breakout_shelf_valid': 640, 'candidate.shelf_valid': 640, 'candidate.compression_valid': 640, 'candidate.active_zone_valid': 640, 'candidate.fake_break_timestamps_valid': 640, 'candidate.trap_event_id_valid': 640, 'candidate.absorption_pass': 640, 'candidate.burst_event_id_valid': 1600, 'candidate.provider_ready': 800, 'candidate.burst_valid': 800, 'candidate.context_pass': 800, 'candidate.data_valid': 42, 'candidate.provider_ready_classic': 42}`
- family_counts: `{'MISC': 4698, 'MIST': 3700, 'MISB': 3700, 'MISR': 3700, 'MISO': 6524}`

## Safety

- orders_xlen_after: `0`
- position_flat: `True`
- risk_execution_or_order_pids: `0`
- broker_calls_executed: false
- order_sent: false
- redis_trading_stream_write_attempted: false

## Next

`A6-LIVE-R2F activation-gate config audit plan / no source patch / no broker call`
