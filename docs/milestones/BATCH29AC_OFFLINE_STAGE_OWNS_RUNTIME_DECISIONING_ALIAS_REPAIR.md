BATCH 29AC OFFLINE STAGE OWNS_RUNTIME_DECISIONING ALIAS REPAIR

generated_at_utc: 2026-05-02T06:35:39.378502+00:00
verdict: DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_OWNS_RUNTIME_DECISIONING_ALIAS_29AC
patch_applied: False
owns_runtime_decisioning_alias_present: True
owns_runtime_decisioning_probe_ok: True
owns_runtime_decisioning_gap_resolved: True
retry_returncode: 2
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'topology_fingerprint'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29AC
repair_path: NEXT_REPLAY_ENGINE_RUNTIME_GAP_AUDIT
next_batch: Batch 29AD — audit/classify next guarded ReplayEngine runtime gap after owns_runtime_decisioning alias repair, still not paper/live enablement.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- none

Proofs:
- run/proofs/proof_offline_stage_owns_runtime_decisioning_alias_repair_29ac.json
- run/proofs/proof_offline_stage_owns_runtime_decisioning_alias_repair_29ac_latest.json
- run/proofs/batch29ac_offline_stage_owns_runtime_decisioning_alias_repair_20260502_120538_driver_proof.json
- etc/replay/parity/offline_stage_owns_runtime_decisioning_alias_repair_29ac.json
