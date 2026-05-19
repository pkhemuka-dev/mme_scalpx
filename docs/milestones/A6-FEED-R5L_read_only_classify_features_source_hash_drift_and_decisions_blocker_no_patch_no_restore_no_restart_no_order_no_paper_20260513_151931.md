# A6-FEED-R5L_read_only_classify_features_source_hash_drift_and_decisions_blocker_no_patch_no_restore_no_restart_no_order_no_paper_20260513_151931

Batch: A6-FEED-R5L

Purpose: read_only_classify_features_source_hash_drift_and_decisions_blocker_no_patch_no_restore_no_restart_no_order_no_paper

Final verdict: PASS_A6_FEED_R5L_FEATURES_DRIFT_CLASSIFIED_NO_PATCH_NO_RESTORE_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only drift classification only; no patch, no restore, no clear/delete, no start/restart/stop, no Redis write, no paper/live, no risk/execution, no broker/order.

Classification:

```json
{
  "current_git_diff_files": [
    "app/mme_scalpx/services/controlled_paper_runtime.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "data/instruments/nfo_instruments.csv"
  ],
  "decisions_stream_xlen": 0,
  "features_compile_ok": true,
  "features_stream_xlen": 313,
  "likely_condition": "R5J_PROVED_FEATURES_SOURCE_CHANGED_DURING_READINESS_WINDOW",
  "next_action": "Do not restart or paper/live. Review diff and decide whether this is expected A6 patch state or cross-lane/source drift.",
  "r5j_drift_files": [
    "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/features.py"
  ],
  "r5j_failures": [
    "checked_sources_unchanged_by_batch"
  ],
  "r5j_final_verdict": "FAIL_A6_FEED_R5J_OWNER_VALIDATION_SAFETY_CHECK",
  "r5j_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5J_read_only_validate_active_feeds_owner_pid_and_readiness_consolidation_no_clear_no_restart_no_order_no_paper_20260513_151546.json",
  "r5j_readiness_failures": [
    "decisions_stream_present"
  ],
  "r5k_final_verdict": "PASS_A6_FEED_R5K_HASH_DRIFT_AND_DECISIONS_BLOCKER_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5k_hash_drift_count": null,
  "r5k_hash_drift_files": null,
  "r5k_likely_condition": "SOURCE_HASH_DRIFT_DETECTED_DURING_R5J_MUST_REVIEW_BEFORE_NEXT_READINESS",
  "r5k_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5K_read_only_extract_r5j_source_hash_drift_and_decisions_blocker_no_patch_no_restart_no_order_no_paper_20260513_151725.json",
  "standard_services": []
}
```

R5J drift:

```json
{
  "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/features.py": {
    "current": "3d8345a47eacef3baf448627710d9f0669235a5df64f9f9042dc2cdbed526117",
    "current_meta": {
      "exists": true,
      "mtime_iso_utc": "2026-05-13T09:45:58.054404+00:00",
      "mtime_ns": 1778665558054404607,
      "path": "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/features.py",
      "sha256": "3d8345a47eacef3baf448627710d9f0669235a5df64f9f9042dc2cdbed526117",
      "size": 318749
    },
    "r5j_after": "3d8345a47eacef3baf448627710d9f0669235a5df64f9f9042dc2cdbed526117",
    "r5j_before": "47e1a298287b055589f5c33efd841ac8a10228fdee0a7ff98bfaee2203c7051d"
  }
}
```

Git diff files:

```json
[
  "app/mme_scalpx/services/controlled_paper_runtime.py",
  "app/mme_scalpx/services/execution.py",
  "app/mme_scalpx/services/features.py",
  "app/mme_scalpx/services/feeds.py",
  "app/mme_scalpx/services/strategy.py",
  "data/instruments/nfo_instruments.csv"
]
```

Required checks:

```json
{
  "checked_sources_unchanged_by_this_batch": true,
  "features_py_currently_compiles": true,
  "latest_r5j_proof_found": true,
  "latest_r5k_proof_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true
}
```

Failures:

```json
[]
```

Proof:
- /home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5L_read_only_classify_features_source_hash_drift_and_decisions_blocker_no_patch_no_restore_no_restart_no_order_no_paper_20260513_151931.json
