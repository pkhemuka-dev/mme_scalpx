Batch 28R-R1 Narrow actual replay-engine module adapter rescue

Date: 2026-05-01

Verdict:
PASS_ACTUAL_REPLAY_ENGINE_MODULE_ADAPTER_28R_R1

Accepted for:
NARROW_ACTUAL_REPLAY_ENGINE_MODULE_ADAPTER_BUILD_ONLY

Reason:
The first 28R command package failed before patching because PROOF_28P_R1_LATEST was referenced but not defined.
28R-R1 fixes that package-level variable omission and reruns the same intended adapter build safely.

Generated:
- bin/actual_replay_engine_module_adapter_28r.py
- etc/replay/parity/actual_replay_engine_module_adapter_28r.json
- run/proofs/proof_actual_replay_engine_module_adapter_28r.json
- run/proofs/proof_actual_replay_engine_module_adapter_28r_latest.json
- run/proofs/proof_actual_replay_engine_module_adapter_28r_r1.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/actual_replay_module_adapter_28r/

Result:
adapter_ready=true
replay_compile_ok=true
likely_module_path_available=true
replay_engine_executed=false
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
full_live_replay_parity=NOT_PROVEN_IN_28R

Next:
Batch 28S — execute narrow actual replay-engine module adapter dry-run, still not paper/live enablement.
