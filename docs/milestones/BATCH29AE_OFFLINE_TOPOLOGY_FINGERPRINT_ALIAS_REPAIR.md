BATCH 29AE OFFLINE TOPOLOGY_FINGERPRINT ALIAS REPAIR

generated_at_utc: 2026-05-02T06:39:09.349810+00:00
verdict: DEFERRED_NEXT_REPLAY_ENGINE_RUNTIME_GAP_AFTER_TOPOLOGY_FINGERPRINT_ALIAS_29AE
patch_applied: True
topology_fingerprint_alias_present: True
topology_fingerprint_probe_ok: True
topology_fingerprint_gap_resolved: True
retry_returncode: 2
retry_runtime_error: AttributeError: 'OfflineReplayTopologyPlan' object has no attribute 'notes'
execution_ok: False
replay_core_executed: False
replay_run_completed: False
comparison_completed: False
full_live_replay_parity: NOT_PROVEN_IN_29AE
repair_path: NEXT_REPLAY_ENGINE_RUNTIME_GAP_AUDIT
next_batch: Batch 29AF — audit/classify next guarded ReplayEngine runtime gap after topology_fingerprint alias repair, still not paper/live enablement.

Safety:
paper_armed_approved: false
live_trading_approved: false
real_order_sent: false
calls_broker_api: false
reads_live_redis: false
writes_live_redis: false

Files changed in this batch:
- app/mme_scalpx/replay/offline_context_shim.py

Proofs:
- run/proofs/proof_offline_topology_fingerprint_alias_repair_29ae.json
- run/proofs/proof_offline_topology_fingerprint_alias_repair_29ae_latest.json
- run/proofs/batch29ae_offline_topology_fingerprint_alias_repair_20260502_120908_driver_proof.json
- etc/replay/parity/offline_topology_fingerprint_alias_repair_29ae.json
