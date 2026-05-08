Batch 28Y Replay core candidate import/signature bridge

Date: 2026-05-01

Verdict:
PASS_REPLAY_CORE_CANDIDATE_IMPORT_SIGNATURE_BRIDGE_28Y

Accepted for:
REPLAY_CORE_CANDIDATE_IMPORT_SIGNATURE_BRIDGE_ONLY

Source:
- 28X proof: run/proofs/proof_guarded_replay_core_execution_adapter_28x_latest.json
- selected candidate: {'kind': 'class', 'methods': ['__call__'], 'module_file': 'app/mme_scalpx/replay/engine.py', 'name': 'ReplayEngineHook', 'score': 9}
- engine file: app/mme_scalpx/replay/engine.py
- 28V callable output root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_execution_28v
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate

Generated:
- bin/guarded_replay_core_candidate_signature_bridge_28y.py
- etc/replay/parity/guarded_replay_core_candidate_signature_bridge_28y.json
- run/proofs/proof_guarded_replay_core_candidate_signature_bridge_28y.json
- run/proofs/proof_guarded_replay_core_candidate_signature_bridge_28y_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/guarded_replay_core_candidate_signature_bridge_28y/

Result:
source_signature_bridge_ready=true
import_execution_ready=true
core_execution_ready=true
candidate_executed=false
replay_core_executed=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
28Y repairs/diagnoses the selected ReplayEngineHook import/signature bridge only.
It does not instantiate or call ReplayEngineHook.
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
full_live_replay_parity=NOT_PROVEN_IN_28Y

Next:
Batch 28Z — execute ReplayEngineHook through guarded import-ready core adapter, still not paper/live enablement.
