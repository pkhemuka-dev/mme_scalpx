# A6-FEED-R5AH_read_only_raw_strategy_log_error_window_extraction_after_frame_distillation_failed_no_patch_no_restart_no_order_no_paper_20260515_105451

Batch: A6-FEED-R5AH

Purpose: read_only_raw_strategy_log_error_window_extraction_after_frame_distillation_failed_no_patch_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5AH_RAW_LOG_ERROR_WINDOWS_CAPTURED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only raw strategy log/error-window extraction only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "candidate_log_count": 6,
  "combined_counts": {
    "argparse_word": 6,
    "consumer_group_word": 70,
    "decision_word": 165,
    "error_word": 1627,
    "exception_word": 22,
    "exit_word": 63,
    "failed_word": 44,
    "feature_word": 5594,
    "file_frame_word": 0,
    "lock_word": 2865,
    "stale_missing_word": 6085,
    "traceback_word": 691
  },
  "decisions_stream_age_ms": 3706163,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 421856,
  "features_stream_xlen": 131,
  "likely_condition": "TRACEBACK_WORD_WAS_PRESENT_WITHOUT_PYTHON_FILE_FRAMES",
  "log_review_count": 6,
  "next_action": "Treat prior traceback-frame path as false/nonstandard. Inspect raw windows manually; next classify exact non-frame error/gate signal. No patch yet.",
  "r5af_final_verdict": "PASS_A6_FEED_R5AF_EXACT_STRATEGY_TRACEBACK_SIGNATURE_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5af_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AF_read_only_extract_exact_strategy_exit_traceback_signature_after_strategy_not_visible_no_patch_no_restart_no_order_no_paper_20260515_105049.json",
  "r5ag_failures": [
    "traceback_frames_extracted"
  ],
  "r5ag_final_verdict": "FAIL_A6_FEED_R5AG_SAFETY_OR_FRAME_DISTILLATION_CHECK",
  "r5ag_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AG_read_only_distill_generic_traceback_frames_source_surface_after_r5af_no_patch_no_restart_no_order_no_paper_20260515_105251.json",
  "raw_window_count": 164,
  "services": []
}
```

Required checks:

```json
{
  "all_watched_sources_compile": true,
  "candidate_logs_found": true,
  "latest_r5af_proof_found": true,
  "latest_r5ag_proof_found": true,
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
  "r5ag_failed_as_frame_distillation_missing_frames": true,
  "raw_log_windows_or_tails_captured": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Artifacts:
- Proof: /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AH_read_only_raw_strategy_log_error_window_extraction_after_frame_distillation_failed_no_patch_no_restart_no_order_no_paper_20260515_105451.json
- Review note: /home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/A6-FEED-R5AH_read_only_raw_strategy_log_error_window_extraction_after_frame_distillation_failed_no_patch_no_restart_no_order_no_paper_20260515_105451_raw_log_error_window_note.md
