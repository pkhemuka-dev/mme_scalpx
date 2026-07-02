# LANE-X-LIVE-R3_RECORD_AND_CANDIDATE_POSITIVE_WATCH_NO_PATCH_NO_REPLAY_NO_ORDER_record_live_growth_and_watch_candidate_positive_evidence_observe_only_20260609_101132

classification: PARTIAL_LIVE_R3_SAFE_BUT_GROWTH_INCOMPLETE_NO_PATCH_NO_REPLAY_NO_ORDER

## Purpose

Live observe-only recording plus candidate-positive watch.

## Candidate evidence

- candidate_positive_seen: False
- candidate_positive_sample_count: 0
- candidate_rows: `[]`

## Growth

- fut: [158, 1202, 1044]
- opt: [898, 7605, 6707]
- features: [4333, 94, -4239]
- decisions: [2196, 1673, -523]
- errors: [10015, 1, -10014]
- provider_runtime: [1584, 10022, 8438]

## Last decisions

- actions: `{'HOLD': 200}`
- top_reasons: `{'hold_only_family_features_consumer_bridge': 200}`

## Safety

- hard_safety_pass: True
- runtime_observe_only: True
- last_safety: `{'exec_stream': 0, 'execution_stream': 0, 'orders': 0, 'risk_stream': 0}`

## Last state

- last_provider: `{'failover_active': 'True', 'family_runtime_mode': 'OBSERVE_ONLY', 'futures_marketdata_status': 'HEALTHY', 'option_context_status': 'UNAVAILABLE', 'selected_option_marketdata_status': 'FAILOVER_ACTIVE'}`
- last_features: `{'frame_valid': '0', 'strategy_mode': 'AUTO', 'system_state': 'DISABLED', 'warmup_complete': '1'}`
- last_snapshots: `{'fut_sync_ok': '1', 'fut_validity': 'OK', 'opt_sync_ok': '1', 'opt_validity': 'OK'}`

## Boundary

- no patch
- no replay
- no risk service start
- no execution service start
- no broker order
- no Redis delete
- no lock delete

## Next decision

`PCHECK_ONLY_MONITOR`
