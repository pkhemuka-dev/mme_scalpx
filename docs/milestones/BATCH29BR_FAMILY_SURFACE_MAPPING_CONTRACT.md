BATCH 29BR FAMILY SURFACE MAPPING CONTRACT

generated_at_utc: 2026-05-03T07:08:05.112738+00:00
verdict: PASS_29BR_FAMILY_SURFACE_MAPPING_CONTRACT_READY
proof_29bq_valid: True
compile_ok: True
safety_ok: true
mapping_contract_ready: True
mapping_row_count: 15
mapping_failure_count: 0
approved_comparable_fields: ['branch', 'family', 'misb', 'misc', 'miso', 'misr', 'mist', 'surface_kind']
family_surface_payload_parity: NOT_PROVEN_MAPPING_CONTRACT_READY
comparison_completed: false
selected_replay_artifact: run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/proof_family_surface_service_path.json
selected_reference_artifact: run/proofs/batch27n_replay_final_acceptance_gate_20260501_142734_inspection/source_snapshot/run/proofs/batch_raw_a_b_freeze_final_v2_20260501_123952_inspection/extracted_bundle/run/proofs/proof_market_session_family_surfaces.json
same_file_exclusion_passed: True
full_live_replay_parity: NOT_PROVEN_IN_29BR
paper_live_status: BLOCKED_NOT_IN_SCOPE
next_batch: Batch 29BS — execute family surface mapped value comparison; still no paper/live enablement.

Artifacts:
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/family_surface_mapping_contract_29br/00_family_surface_strict_comparison_contract.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/family_surface_mapping_contract_29br/01_mapping_summary.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/family_surface_mapping_contract_29br/02_next_value_comparison_plan_29bs.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/family_surface_mapping_contract_29br/03_evidence_chain_snapshot.json
- run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/family_surface_mapping_contract_29br/04_operator_summary.md
- run/proofs/proof_family_surface_mapping_contract_29br.json
- run/proofs/proof_family_surface_mapping_contract_29br_latest.json
- etc/replay/parity/family_surface_mapping_contract_29br.json

Boundary:
- code_patch_applied: false
- files_changed: []
- starts_services: false
- reads_live_redis: false
- writes_live_redis: false
- calls_broker_api: false
- paper_armed_approved: false
- live_trading_approved: false
- full_live_replay_parity: NOT_PROVEN_IN_29BR

Conclusion:
29BR freezes the mapping contract only. It does not execute value parity and does not approve paper/live trading.
