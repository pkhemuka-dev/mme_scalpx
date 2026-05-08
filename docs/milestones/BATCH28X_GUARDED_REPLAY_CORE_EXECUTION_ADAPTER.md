Batch 28X Guarded replay core execution adapter

Date: 2026-05-01

Verdict:
DEFERRED_REPLAY_CORE_CANDIDATE_IMPORT_OR_SIGNATURE_REQUIRED_28X

Accepted for:
GUARDED_REPLAY_CORE_EXECUTION_ADAPTER_BUILD_ONLY

Source:
- 28W proof: run/proofs/proof_concrete_replay_engine_core_wiring_contract_28w_latest.json
- selected candidate: {'kind': 'class', 'methods': ['__call__'], 'module_file': 'app/mme_scalpx/replay/engine.py', 'name': 'ReplayEngineHook', 'score': 9}
- 28V callable output root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_execution_28v
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate

Generated:
- bin/guarded_replay_core_execution_adapter_28x.py
- etc/replay/parity/guarded_replay_core_execution_adapter_28x.json
- run/proofs/proof_guarded_replay_core_execution_adapter_28x.json
- run/proofs/proof_guarded_replay_core_execution_adapter_28x_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_core_execution_adapter_28x/

Result:
core_adapter_ready=false
candidate_executed=false
replay_core_executed=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
28X builds and proves the guarded core execution adapter only.
It does not instantiate/call the replay core candidate.
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
full_live_replay_parity=NOT_PROVEN_IN_28X

Next:
Batch 28Y — repair selected replay core candidate import/signature bridge, still not paper/live enablement.
