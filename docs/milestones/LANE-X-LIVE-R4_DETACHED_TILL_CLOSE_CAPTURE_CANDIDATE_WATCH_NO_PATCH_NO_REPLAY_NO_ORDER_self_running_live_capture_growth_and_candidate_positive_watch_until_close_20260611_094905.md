# LANE-X-LIVE-R4_DETACHED_TILL_CLOSE_CAPTURE_CANDIDATE_WATCH_NO_PATCH_NO_REPLAY_NO_ORDER_self_running_live_capture_growth_and_candidate_positive_watch_until_close_20260611_094905

classification: PARTIAL_LIVE_R4_SAFE_BUT_GROWTH_INCOMPLETE_NO_PATCH_NO_REPLAY_NO_ORDER

## Purpose

Detached all-day live observe-only capture growth and candidate-positive watch until close.

## Candidate evidence

- candidate_positive_seen: False
- candidate_positive_sample_count: 0
- candidate_rows: `[]`

## Growth

- fut: [101, 0, -101]
- opt: [525, 2117, 1592]
- features: [4286, 0, -4286]
- decisions: [1993, 0, -1993]
- errors: [10015, 0, -10015]
- provider_runtime: [918, 0, -918]

## Last decisions

- actions: `{}`
- top_reasons: `{}`

## Safety

- hard_safety_pass: True
- runtime_observe_only: False
- last_safety: `{'exec_stream': 0, 'execution_stream': 0, 'orders': 0, 'risk_stream': 0}`

## Last state

- last_provider: `{'failover_active': '', 'family_runtime_mode': '', 'futures_marketdata_status': '', 'option_context_status': '', 'selected_option_marketdata_status': ''}`
- last_features: `{'frame_valid': '', 'strategy_mode': '', 'system_state': '', 'warmup_complete': ''}`
- last_snapshots: `{'fut_sync_ok': '', 'fut_validity': '', 'opt_sync_ok': '', 'opt_validity': ''}`

## Boundary

- no patch
- no replay
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete

## Next decision

`PCHECK_ONLY_THEN_PSEAL_AT_CLOSE`
