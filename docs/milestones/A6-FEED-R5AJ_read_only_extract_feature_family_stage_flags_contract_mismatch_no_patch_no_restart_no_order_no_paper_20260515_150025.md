# A6-FEED-R5AJ_read_only_extract_feature_family_stage_flags_contract_mismatch_no_patch_no_restart_no_order_no_paper_20260515_150025

Batch: A6-FEED-R5AJ

Purpose: read_only_extract_feature_family_stage_flags_contract_mismatch_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5AJ_FEATURE_FAMILY_STAGE_FLAGS_CONTRACT_MISMATCH_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only feature-family stage_flags contract mismatch extraction only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "contract_detail_count": 5,
  "decisions_stream_age_ms": 18440774,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 15155714,
  "features_stream_xlen": 131,
  "likely_condition": "FEATURE_FAMILY_STAGE_FLAGS_CONTRACT_MISMATCH_BLOCKS_STRATEGY_DECISION_PRODUCTION",
  "next_action": "Prepare narrow patch plan to align feature-family stage_flags producer/contract/consumer surfaces only. No restart/paper/live.",
  "override_reason": "Top signature shows FeatureFamilyContractError stage_flags keys mismatch, which is stronger than the single consumer_group category count.",
  "r5ai_r2_final_verdict": "PASS_A6_FEED_R5AI_R2_EXACT_RAW_SIGNATURES_DISTILLED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ai_r2_likely_condition_reported": "RAW_SIGNATURE_POINTS_TO_CONSUMER_GROUP_GATE",
  "r5ai_r2_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AI-R2_clipboard_safe_distill_exact_non_frame_error_gate_signature_from_r5ah_raw_windows_no_patch_no_restart_no_order_no_paper_20260515_105722.json",
  "services": []
}
```

Required checks:

```json
{
  "all_feature_family_sources_compile": true,
  "all_watched_sources_compile": true,
  "contract_error_details_extracted": true,
  "feature_family_sources_inspected": true,
  "feature_family_sources_unchanged_by_this_batch": true,
  "latest_r5ai_r2_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "r5ai_r2_passed": true,
  "top_signature_contains_feature_family_contract_error": true,
  "top_signature_contains_stage_flags_mismatch": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AJ_read_only_extract_feature_family_stage_flags_contract_mismatch_no_patch_no_restart_no_order_no_paper_20260515_150025.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AJ_read_only_extract_feature_family_stage_flags_contract_mismatch_no_patch_no_restart_no_order_no_paper_20260515_150025_stage_flags_contract_mismatch_note.md
