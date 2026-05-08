Batch 28T Replay-engine callable adapter discovery

Date: 2026-05-01

Verdict:
DEFERRED_PROVEN_REPLAY_ENGINE_CALLABLE_REQUIRED_28T

Accepted for:
ACTUAL_REPLAY_ENGINE_CALLABLE_DISCOVERY_AND_ADAPTER_CONTRACT_ONLY

Source:
- 28S proof: run/proofs/proof_actual_replay_engine_module_adapter_execution_28s_latest.json
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate
- replay modules inspected by import/introspection

Generated:
- bin/actual_replay_engine_callable_adapter_28t.py
- etc/replay/parity/actual_replay_engine_callable_adapter_28t.json
- run/proofs/proof_actual_replay_engine_callable_adapter_28t.json
- run/proofs/proof_actual_replay_engine_callable_adapter_28t_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/actual_replay_callable_adapter_28t/

Result:
callable_adapter_ready=false
selected_callable=None
candidate_count=0
replay_engine_invoked=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
28T discovers and contracts a replay callable only.
It does not invoke the replay engine.
It does not produce replay outputs.
It does not compare replay/live parity.

Safety:
starts_services=false
reads_live_redis=false
writes_live_redis=false
calls_broker_api=false
paper_armed_approved=false
live_trading_approved=false
execution_arming_created=false
real_order_sent=false
production_doctrine_changed=false
full_live_replay_parity=NOT_PROVEN_IN_28T

Next:
Batch 28U — repair replay callable surface or add explicit offline replay callable, still not paper/live enablement.
