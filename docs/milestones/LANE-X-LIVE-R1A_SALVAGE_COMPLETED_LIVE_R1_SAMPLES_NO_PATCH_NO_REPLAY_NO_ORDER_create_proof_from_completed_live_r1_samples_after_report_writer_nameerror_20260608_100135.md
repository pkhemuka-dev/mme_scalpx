# LANE-X-LIVE-R1A_SALVAGE_COMPLETED_LIVE_R1_SAMPLES_NO_PATCH_NO_REPLAY_NO_ORDER_create_proof_from_completed_live_r1_samples_after_report_writer_nameerror_20260608_100135

classification: PASS_LIVE_R1A_SALVAGED_OBSERVE_GROWTH_DECISIONS_NO_NEW_ERRORS_NO_ORDER

## Purpose

Salvage proof from completed LIVE-R1 detached samples after report-writer NameError.

## Source

- src_dir: `run/audits/LANE-X-LIVE-R1_SAFE_10MIN_OBSERVE_CHECK_NO_PATCH_NO_REPLAY_NO_ORDER_verify_live_market_observe_only_capture_growth_feature_validity_strategy_errors_and_no_order_safety_20260608_095442`
- samples: `run/audits/LANE-X-LIVE-R1_SAFE_10MIN_OBSERVE_CHECK_NO_PATCH_NO_REPLAY_NO_ORDER_verify_live_market_observe_only_capture_growth_feature_validity_strategy_errors_and_no_order_safety_20260608_095442/samples.jsonl`
- sample_count: 6
- first_ts: 2026-06-08T09:54:43.127047
- last_ts: 2026-06-08T09:57:15.234098

## Live observe findings

- hard_safety_pass: True
- current_safety_pass: True
- runtime_observe_only: True
- marketdata_ok: True
- growth_ok: True
- feature_growth_seen: True
- decision_growth_seen: True
- no_error_growth: True

## Deltas

`{'decisions': [2439, 2598, 159], 'errors': [1, 1, 0], 'features': [22, 54, 32], 'provider_runtime': [2308, 2813, 505], 'ticks_fut': [262, 321, 59], 'ticks_fut_zerodha': [262, 321, 59], 'ticks_opt': [1328, 1609, 281], 'ticks_opt_selected_zerodha': [1340, 1621, 281]}`

## Sample quality

- valid_feature_sample_count: 5
- ok_snapshot_sample_count: 2
- disabled_sample_count: 1
- unsynced_or_invalid_sample_count: 4

## Last state

- last_provider: `{'execution_fallback_status': 'DISABLED', 'execution_primary_status': 'HEALTHY', 'failover_active': 'True', 'family_runtime_mode': 'OBSERVE_ONLY', 'futures_marketdata_status': 'HEALTHY', 'option_context_status': 'UNAVAILABLE', 'selected_option_marketdata_status': 'FAILOVER_ACTIVE'}`
- last_features: `{'frame_ts_ns': '1780892831432384947', 'frame_valid': '1', 'strategy_mode': 'AUTO', 'system_state': 'SCANNING', 'warmup_complete': '1'}`
- last_snapshots: `{'fut_sync_ok': '0', 'fut_validity': 'INVALID_MEMBER', 'opt_sync_ok': '0', 'opt_validity': 'INVALID_MEMBER'}`

## Current safety

- orders: 0
- risk_stream: 0
- execution_stream: 0
- exec_stream: 0
- replay_proc: 0
- risk_proc: 0
- execution_proc: 0

## Boundary

- no patch
- no replay
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete

## Next decision

`CONTINUE_OBSERVE_ONLY_AND_PSEAL_AT_MARKET_CLOSE`
