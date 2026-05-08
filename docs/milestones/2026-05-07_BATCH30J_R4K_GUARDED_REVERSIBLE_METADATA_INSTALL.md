# Batch 30J-R4K — Guarded Reversible Metadata Install + Dry Selector/CLI Validation

Verdict: REVIEW_REQUIRED

Health: REVIEW_REQUIRED

Classification: METADATA_INSTALLED_AND_DRY_SELECTOR_CLI_VALIDATED_WITH_ONE_DATE_REVIEW

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Metadata installed: True

Install actions: [
  {
    "source": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/00_selector_available_dates_candidate.json",
    "target": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_available_dates.json",
    "backup": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/guarded_reversible_install_30j_r4k_20260507_151309/backup_before_reversible_install_actual/selector_available_dates.json",
    "source_exists": true,
    "target_exists_before": false,
    "source_sha256_before": "53eb1decc51ad1f905371a205dbbdac2322ab895eb64fe71cb742ce83b5ff5e6",
    "target_sha256_before": null,
    "installed": true,
    "ok": true,
    "backup_written": false,
    "target_absent_before_marker": true,
    "target_exists_after": true,
    "target_sha256_after": "53eb1decc51ad1f905371a205dbbdac2322ab895eb64fe71cb742ce83b5ff5e6"
  },
  {
    "source": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/01_replay_dataset_manifest_candidate.json",
    "target": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/replay_dataset_manifest_candidate.json",
    "backup": "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/guarded_reversible_install_30j_r4k_20260507_151309/backup_before_reversible_install_actual/replay_dataset_manifest_candidate.json",
    "source_exists": true,
    "target_exists_before": false,
    "source_sha256_before": "1d2a21d7dd997d6c7709968a94d1aaf6872a86e565c1debeec845384836f8ad0",
    "target_sha256_before": null,
    "installed": true,
    "ok": true,
    "backup_written": false,
    "target_absent_before_marker": true,
    "target_exists_after": true,
    "target_sha256_after": "1d2a21d7dd997d6c7709968a94d1aaf6872a86e565c1debeec845384836f8ad0"
  }
]

Selector accepted: True via ReplaySelector._resolve_dates

Dry argparse ok: True

Rollback actions: []

Artifact files: [
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/guarded_reversible_install_30j_r4k_20260507_151309/13_guarded_reversible_metadata_install_validation.json",
  "run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0/selector_metadata_candidate_30j_r4g/guarded_reversible_install_30j_r4k_20260507_151309/14_30j_r4l_readiness.json"
]

Blockers: []

Review: [
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_ACCEPTED_FOR_CONTROLLED_NEXT_STEP"
]

Next: Review one-date limitation, then run 30J-R4L final replay-command safety gate; no broker/order/live.

Safety: metadata install only; no replay execution, no Redis write/delete, no service start/stop, no paper/live, no orders.
