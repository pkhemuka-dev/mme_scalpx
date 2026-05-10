# Batch 30J-R5AO — Guarded Historic Source-Shape Audit

Verdict: `PASS_SOURCE_SHAPE_CANDIDATES_READY_FOR_GUARDED_MATERIALIZATION_PLAN`
Classification: `INGESTABLE_HISTORIC_SOURCE_GROUPS_FOUND`

Target dates:
[
  "2026-04-25",
  "2026-05-01",
  "2026-05-02",
  "2026-05-03",
  "2026-05-04",
  "2026-05-06",
  "2026-05-08",
  "2000-00-00"
]

Repository dates:
[
  "2026-04-17"
]

Strong dates:
[
  {
    "date": "2026-04-25",
    "strong_group_count": 13,
    "complete_group_count": 13
  },
  {
    "date": "2026-05-01",
    "strong_group_count": 3,
    "complete_group_count": 5
  },
  {
    "date": "2026-05-02",
    "strong_group_count": 3,
    "complete_group_count": 3
  },
  {
    "date": "2026-05-03",
    "strong_group_count": 1,
    "complete_group_count": 5
  },
  {
    "date": "2026-05-04",
    "strong_group_count": 2,
    "complete_group_count": 2
  },
  {
    "date": "2026-05-06",
    "strong_group_count": 1,
    "complete_group_count": 2
  },
  {
    "date": "2026-05-08",
    "strong_group_count": 1,
    "complete_group_count": 3
  },
  {
    "date": "2000-00-00",
    "strong_group_count": 1,
    "complete_group_count": 3
  }
]

Date audit summary:
{
  "2026-04-25": {
    "input_file_count_from_r5an": 23930,
    "inspected_file_count": 900,
    "group_count": 18,
    "strong_group_count": 13,
    "complete_group_count": 13,
    "best_group_root": "run/evidence_bundles/mme_scalpx_integrity_raw_replay_bundle_v2_20260502_103549"
  },
  "2026-05-01": {
    "input_file_count_from_r5an": 180037,
    "inspected_file_count": 900,
    "group_count": 14,
    "strong_group_count": 3,
    "complete_group_count": 5,
    "best_group_root": "run/evidence_bundles/mme_integrity_surface_raw_replay_evidence_20260502_102410"
  },
  "2026-05-02": {
    "input_file_count_from_r5an": 72883,
    "inspected_file_count": 900,
    "group_count": 5,
    "strong_group_count": 3,
    "complete_group_count": 3,
    "best_group_root": "run/evidence_bundles/mme_integrity_surface_raw_replay_evidence_20260502_102410"
  },
  "2026-05-03": {
    "input_file_count_from_r5an": 3827,
    "inspected_file_count": 900,
    "group_count": 32,
    "strong_group_count": 1,
    "complete_group_count": 5,
    "best_group_root": "run/evidence_bundles/mme_scalpx_audit_bundle_20260503_115714"
  },
  "2026-05-04": {
    "input_file_count_from_r5an": 4104,
    "inspected_file_count": 900,
    "group_count": 5,
    "strong_group_count": 2,
    "complete_group_count": 2,
    "best_group_root": "run/evidence_bundles/mme_scalpx_audit_bundle_20260504_091432"
  },
  "2026-05-06": {
    "input_file_count_from_r5an": 2193,
    "inspected_file_count": 900,
    "group_count": 14,
    "strong_group_count": 1,
    "complete_group_count": 2,
    "best_group_root": "run/evidence_bundles/mme_scalpx_audit_bundle_20260506_104201"
  },
  "2026-05-08": {
    "input_file_count_from_r5an": 2865,
    "inspected_file_count": 900,
    "group_count": 18,
    "strong_group_count": 1,
    "complete_group_count": 3,
    "best_group_root": "run/evidence_bundles/mme_scalpx_audit_bundle_20260508_104248"
  },
  "2000-00-00": {
    "input_file_count_from_r5an": 4078,
    "inspected_file_count": 900,
    "group_count": 23,
    "strong_group_count": 1,
    "complete_group_count": 3,
    "best_group_root": "run/evidence_bundles/mme_scalpx_integrity_raw_replay_bundle_v2_20260502_103549"
  }
}

No replay execution.
No repository mutation.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Run R5AP guarded materialization plan for top strong candidate dates; no repository mutation until plan validates.
