Batch 28W Concrete replay-engine core wiring contract

Date: 2026-05-01

Verdict:
PASS_CONCRETE_REPLAY_ENGINE_CORE_WIRING_CONTRACT_28W

Accepted for:
CONCRETE_REPLAY_ENGINE_CORE_WIRING_CONTRACT_ONLY

Source:
- 28V proof: run/proofs/proof_explicit_offline_replay_callable_execution_28v_latest.json
- 28V execution root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/explicit_offline_replay_callable_execution_28v
- dataset candidate root: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/dataset_candidate
- replay core files: app/mme_scalpx/replay/*

Generated:
- etc/replay/parity/concrete_replay_engine_core_wiring_contract_28w.json
- run/proofs/proof_concrete_replay_engine_core_wiring_contract_28w.json
- run/proofs/proof_concrete_replay_engine_core_wiring_contract_28w_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/concrete_replay_engine_core_wiring_contract_28w/

Result:
recommended_core_wiring_path=SELECTED_CORE_CANDIDATE_REQUIRES_EXECUTION_ADAPTER
core_candidate_count=97
selected_core_candidate={'module_file': 'app/mme_scalpx/replay/engine.py', 'kind': 'class', 'name': 'ReplayEngineHook', 'methods': ['__call__'], 'score': 9}
replay_compile_ok=true
replay_core_executed=false
replay_run_completed=false
comparison_completed=false

Important interpretation:
28W does not execute replay core.
28W prepares the concrete wiring contract from 28V callable outputs to replay core surfaces.
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
full_live_replay_parity=NOT_PROVEN_IN_28W

Next:
Batch 28X — build guarded core execution adapter around selected replay core candidate, still not paper/live enablement.
