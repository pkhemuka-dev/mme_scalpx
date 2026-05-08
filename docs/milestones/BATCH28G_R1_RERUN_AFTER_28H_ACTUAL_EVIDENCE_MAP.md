Batch 28G-R1 Rerun actual observe_only evidence-map generation after 28H

Date: 2026-05-01

Verdict:
PASS_OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_GENERATED_28G_R1_AFTER_28H

Accepted for:
RERUN_28G_AFTER_28H_MISSING_OUTPUT_GENERATION

Inputs:
- run/proofs/proof_observe_only_missing_market_session_evidence_28h_latest.json
- run/proofs/proof_market_session_live_stream_inventory.json
- run/proofs/proof_market_session_live_hash_inventory.json
- run/proofs/proof_market_session_provider_health_snapshot.json
- run/proofs/proof_market_session_selected_option_context.json
- run/proofs/proof_market_session_dhan_oi_ladder_context.json
- existing Batch 28G generator/proof scripts

Outputs inspected:
- run/proofs/proof_observe_only_actual_evidence_map_generation_28g_latest.json
- etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json
- etc/replay/parity/observe_only_actual_generated_evidence_map.json
- run/proofs/observe_only_actual_evidence_map_missing_report_28g.json

Result:
final_map_published=true
final_map_present=true
missing_count=5

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
full_live_replay_parity=NOT_PROVEN_IN_28G_R1

Next:
Batch 28F rerun/close package collection from generated final map.
