Batch 28Z ReplayEngineHook guarded execution

Date: 2026-05-01

Verdict:
FAIL_REPLAY_ENGINE_HOOK_GUARDED_EXECUTION_28Z

Accepted for:
GUARDED_REPLAY_ENGINE_HOOK_EXECUTION_ONLY

Source:
- 28Y proof: run/proofs/proof_guarded_replay_core_candidate_signature_bridge_28y_latest.json
- selected candidate: {'kind': 'class', 'methods': ['__call__'], 'module_file': 'app/mme_scalpx/replay/engine.py', 'name': 'ReplayEngineHook', 'score': 9}
- engine file: app/mme_scalpx/replay/engine.py
- 28V callable output root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_execution_28v
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate

Generated:
- bin/execute_replay_engine_hook_guarded_28z.py
- etc/replay/parity/replay_engine_hook_guarded_execution_28z.json
- run/proofs/proof_replay_engine_hook_guarded_execution_28z.json
- run/proofs/proof_replay_engine_hook_guarded_execution_28z_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_engine_hook_guarded_execution_28z/

Result:
preflight_ok=false
execution_ok=false
candidate_executed=false
replay_core_executed=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
28Z executes only the guarded ReplayEngineHook candidate if argument binding is fully satisfied.
Replay/live parity remains not proven.
No paper/live enablement is allowed or performed.

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
full_live_replay_parity=NOT_PROVEN_IN_28Z

Next:
Repair 28Z guarded execution before replay-output inspection.
