Batch 28Z-R2 Repair exec_static self-veto and retry guarded ReplayEngineHook execution

Date: 2026-05-01

Verdict:
DEFERRED_REPLAY_ENGINE_HOOK_ARGUMENT_BINDING_REQUIRED_28Z_R2

Accepted for:
GUARDED_REPLAY_ENGINE_HOOK_EXECUTION_RETRY_ONLY

Source:
- 28Z-R1 proof: run/proofs/proof_replay_engine_hook_preflight_gate_audit_28z_r1_latest.json
- failed condition repaired: ['exec_static_ok']
- selected candidate: {'kind': 'class', 'methods': ['__call__'], 'module_file': 'app/mme_scalpx/replay/engine.py', 'name': 'ReplayEngineHook', 'score': 9}
- 28V callable output root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_execution_28v
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate

Generated:
- bin/execute_replay_engine_hook_guarded_28z_r2.py
- etc/replay/parity/replay_engine_hook_guarded_execution_28z_r2.json
- run/proofs/proof_replay_engine_hook_guarded_execution_28z_r2.json
- run/proofs/proof_replay_engine_hook_guarded_execution_28z_r2_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_engine_hook_guarded_execution_28z_r2/

Result:
preflight_ok=true
execution_ok=false
candidate_executed=false
replay_core_executed=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
28Z-R2 repairs the 28Z execution-script self-veto and retries only the guarded offline candidate path.
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
full_live_replay_parity=NOT_PROVEN_IN_28Z_R2

Next:
Batch 29A — repair ReplayEngineHook argument binding before core execution, still not paper/live enablement.
