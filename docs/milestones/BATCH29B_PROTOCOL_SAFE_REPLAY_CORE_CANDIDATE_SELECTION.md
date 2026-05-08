Batch 29B Protocol-safe replay-core candidate selection

Date: 2026-05-01

Verdict:
PASS_PROTOCOL_SAFE_CONCRETE_REPLAY_CORE_CANDIDATE_SELECTION_29B

Accepted for:
PROTOCOL_SAFE_CONCRETE_REPLAY_CORE_CANDIDATE_SELECTION_ONLY

Source:
- 29A proof: run/proofs/proof_replay_engine_hook_argument_binding_audit_29a_latest.json
- 29A result_error: TypeError: Protocols cannot be instantiated
- replay source dir: app/mme_scalpx/replay/

Generated:
- bin/protocol_safe_replay_core_candidate_selector_29b.py
- etc/replay/parity/protocol_safe_replay_core_candidate_selection_29b.json
- run/proofs/proof_protocol_safe_replay_core_candidate_selection_29b.json
- run/proofs/proof_protocol_safe_replay_core_candidate_selection_29b_latest.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/protocol_safe_replay_core_candidate_selection_29b/

Result:
concrete_candidate_selected=true
selected_candidate={'bases': [], 'call_args': [], 'excluded_reason': 'low_score_or_no_executable_method', 'has_call': False, 'has_run_or_execute': True, 'is_abstract': False, 'is_protocol': False, 'kind': 'class', 'lineno': 147, 'methods': ['__init__', 'build_context', 'execute', '_execute_stage', '_run_hooks', '_transition'], 'module_file': 'app/mme_scalpx/replay/engine.py', 'name': 'ReplayEngine', 'run_args': ['self', 'run_context', 'topology_plan', 'stage_executor'], 'score': 25}
candidate_count=220
excluded_protocol_count=5
excluded_abstract_count=0
candidate_executed=false
replay_core_executed=false
replay_run_completed=false
comparison_completed=false

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
full_live_replay_parity=NOT_PROVEN_IN_29B

Next:
Batch 29C — build guarded adapter for selected concrete replay-core candidate, still not paper/live enablement.
