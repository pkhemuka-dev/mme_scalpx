# LANE-X-LIVE-R2_30MIN_CANDIDATE_POSITIVE_WATCH_NO_PATCH_NO_ORDER_watch_live_decisions_for_candidate_positive_evidence_observe_only_20260608_101421

classification: PARTIAL_LIVE_R2_SAFE_BUT_GROWTH_INCOMPLETE_NO_ORDER

## Purpose

30-minute live observe-only candidate-positive watch.

## Candidate-positive evidence

- candidate_positive_seen: False
- candidate_positive_sample_count: 0
- candidate_rows: `[]`

## Growth

- fut: [17, 466, 449]
- opt: [144, 2618, 2474]
- features: [16, 299, 283]
- decisions: [3529, 119, -3410]
- errors: [1, 14, 13]

## Safety

- hard_safety_pass: True
- runtime_observe_only: True
- last_safety: `{'exec_stream': 0, 'execution_stream': 0, 'orders': 0, 'risk_stream': 0}`

## Last state

- last_provider: `{'failover_active': 'True', 'family_runtime_mode': 'OBSERVE_ONLY', 'futures_marketdata_status': 'HEALTHY', 'option_context_status': 'UNAVAILABLE', 'selected_option_marketdata_status': 'FAILOVER_ACTIVE'}`
- last_features: `{'frame_valid': '1', 'strategy_mode': 'AUTO', 'system_state': 'SCANNING', 'warmup_complete': '1'}`
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
