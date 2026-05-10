# Batch 30J-R5AS — Row-Level Non-Repo Source Date Discovery

Verdict: `PASS_ROW_LEVEL_NON_REPO_DATE_CANDIDATES_FOUND`
Classification: `ROW_LEVEL_TRADING_DATES_OUTSIDE_REPLAY_REPOSITORY_DISCOVERED`

Repository dates:
[
  "2026-04-17"
]

Files discovered:
`50000`

Files scanned:
`50000`

Accepted file count:
`24601`

Strong file count:
`1`

Date candidate count:
`314`

Top ranked dates:
[
  {
    "date": "2026-04-18",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 84466,
    "file_count": 16867,
    "strong_file_count": 0,
    "required_presence": {
      "features": true,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 3875,
      "orders_no_order": 138,
      "redis_stream": 142,
      "features": 2608,
      "strategy": 2423,
      "dataset_manifest": 7136,
      "family_surfaces": 5299,
      "option_ticks": 2458,
      "risk": 538,
      "feed_snapshot": 102,
      "execution_shadow": 28
    },
    "provenance_counts": {
      "evidence_bundle": 16867
    }
  },
  {
    "date": "2026-04-25",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 11546,
    "file_count": 2287,
    "strong_file_count": 0,
    "required_presence": {
      "features": false,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 1303,
      "orders_no_order": 139,
      "redis_stream": 153,
      "strategy": 256,
      "risk": 57,
      "dataset_manifest": 128,
      "family_surfaces": 624,
      "execution_shadow": 16,
      "provider_runtime": 18
    },
    "provenance_counts": {
      "evidence_bundle": 2287
    }
  },
  {
    "date": "2026-04-19",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 8171,
    "file_count": 1608,
    "strong_file_count": 0,
    "required_presence": {
      "features": true,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 151,
      "orders_no_order": 23,
      "redis_stream": 27,
      "dataset_manifest": 1143,
      "family_surfaces": 1077,
      "features": 194,
      "option_ticks": 443,
      "feed_snapshot": 34,
      "strategy": 181,
      "risk": 4,
      "execution_shadow": 4
    },
    "provenance_counts": {
      "evidence_bundle": 1608
    }
  },
  {
    "date": "2026-05-01",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 7266,
    "file_count": 1427,
    "strong_file_count": 0,
    "required_presence": {
      "features": true,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "execution_shadow": 634,
      "redis_stream": 549,
      "provider_runtime": 87,
      "dhan_context": 139,
      "family_surfaces": 358,
      "dataset_manifest": 262,
      "unknown": 322,
      "risk": 241,
      "strategy": 342,
      "features": 65,
      "futures_ticks": 34,
      "option_ticks": 28,
      "orders_no_order": 165,
      "feed_snapshot": 21
    },
    "provenance_counts": {
      "evidence_bundle": 1427
    }
  },
  {
    "date": "2026-04-23",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 5971,
    "file_count": 1180,
    "strong_file_count": 0,
    "required_presence": {
      "features": false,
      "strategy": true,
      "risk": false,
      "execution_shadow": false
    },
    "surface_counts": {
      "unknown": 595,
      "orders_no_order": 114,
      "redis_stream": 114,
      "family_surfaces": 400,
      "dataset_manifest": 146,
      "option_ticks": 35,
      "strategy": 122,
      "feed_snapshot": 6
    },
    "provenance_counts": {
      "evidence_bundle": 1180
    }
  },
  {
    "date": "2026-04-26",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 5816,
    "file_count": 1141,
    "strong_file_count": 0,
    "required_presence": {
      "features": false,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 564,
      "family_surfaces": 431,
      "provider_runtime": 68,
      "redis_stream": 27,
      "dataset_manifest": 28,
      "strategy": 131,
      "risk": 4,
      "execution_shadow": 4
    },
    "provenance_counts": {
      "evidence_bundle": 1141
    }
  },
  {
    "date": "2026-04-01",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 5621,
    "file_count": 1098,
    "strong_file_count": 0,
    "required_presence": {
      "features": true,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 267,
      "orders_no_order": 23,
      "redis_stream": 27,
      "dataset_manifest": 343,
      "features": 339,
      "strategy": 126,
      "family_surfaces": 309,
      "risk": 4,
      "execution_shadow": 4
    },
    "provenance_counts": {
      "evidence_bundle": 1098
    }
  },
  {
    "date": "2026-04-16",
    "date_classification": "STRONG_NON_REPO_REPLAY_CANDIDATE",
    "candidate_score": 5155,
    "file_count": 980,
    "strong_file_count": 1,
    "required_presence": {
      "features": true,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 332,
      "strategy": 198,
      "redis_stream": 203,
      "orders_no_order": 67,
      "features": 62,
      "risk": 107,
      "execution_shadow": 67,
      "feed_snapshot": 19,
      "dataset_manifest": 63,
      "family_surfaces": 277
    },
    "provenance_counts": {
      "evidence_bundle": 980
    }
  },
  {
    "date": "2026-04-27",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 4911,
    "file_count": 960,
    "strong_file_count": 0,
    "required_presence": {
      "features": false,
      "strategy": true,
      "risk": true,
      "execution_shadow": true
    },
    "surface_counts": {
      "unknown": 559,
      "dataset_manifest": 26,
      "strategy": 117,
      "family_surfaces": 307,
      "risk": 4,
      "execution_shadow": 4,
      "redis_stream": 6
    },
    "provenance_counts": {
      "evidence_bundle": 960
    }
  },
  {
    "date": "2026-04-03",
    "date_classification": "WEAK_NON_REPO_REVIEW",
    "candidate_score": 3277,
    "file_count": 647,
    "strong_file_count": 0,
    "required_presence": {
      "features": true,
      "strategy": true,
      "risk": false,
      "execution_shadow": false
    },
    "surface_counts": {
      "dataset_manifest": 321,
      "features": 339,
      "unknown": 5,
      "family_surfaces": 180,
      "strategy": 72
    },
    "provenance_counts": {
      "evidence_bundle": 647
    }
  }
]

No replay execution.
No repository mutation.
No staging materialization.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Run R5AT source-group planner for top row-level non-repo date candidates; no repository mutation.
