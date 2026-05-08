Batch 28S Execute narrow actual replay-engine module adapter dry-run

Date: 2026-05-01

Verdict:
DEFERRED_ACTUAL_REPLAY_ENGINE_NOT_INVOKED_BY_28R_ADAPTER_28S

Accepted for:
NARROW_ACTUAL_REPLAY_ENGINE_MODULE_ADAPTER_EXECUTION_ATTEMPT

Source:
- 28R/28R-R1 adapter proof: run/proofs/proof_actual_replay_engine_module_adapter_28r_latest.json
- adapter script: bin/actual_replay_engine_module_adapter_28r.py
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate

Generated:
- etc/replay/parity/actual_replay_engine_module_adapter_execution_28s.json
- run/proofs/proof_actual_replay_engine_module_adapter_execution_28s.json
- run/proofs/proof_actual_replay_engine_module_adapter_execution_28s_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/actual_replay_module_adapter_execution_28s/

Result:
adapter_execution_ok=true
actual_engine_executed=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
If verdict is DEFERRED, the adapter executed safely but did not invoke the actual replay engine.
Replay/live parity remains not proven.

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
full_live_replay_parity=NOT_PROVEN_IN_28S

Next:
Batch 28T — extend the narrow module adapter to invoke a proven replay-engine callable, still not paper/live enablement.
