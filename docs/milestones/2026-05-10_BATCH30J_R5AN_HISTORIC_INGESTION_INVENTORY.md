# Batch 30J-R5AN — Historic Date Ingestion Source Inventory

Verdict: `PASS_HISTORIC_INGESTION_CANDIDATES_FOUND`
Classification: `MORE_HISTORIC_DATES_EXIST_OUTSIDE_REPLAY_REPOSITORY`

Current replay repository dates:
[
  "2026-04-17"
]

Candidate file count:
`200831`

Not-installed candidate date count:
`80`

Top not-installed candidates:
[
  {
    "date": "2026-04-25",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 23930,
    "surface_counts": {
      "unknown": 17985,
      "strategy": 2068,
      "risk": 293,
      "redis_stream": 473,
      "dataset_manifest": 498,
      "execution_shadow": 523,
      "features": 714,
      "feed_snapshot": 320,
      "family_surfaces": 1585,
      "provider_runtime": 348,
      "orders_no_order": 21,
      "option_ticks": 40,
      "dhan_context": 19,
      "futures_ticks": 2
    },
    "roots": {
      "run/live_capture": 5,
      "run/evidence_bundles": 9512,
      "run/replay/parity": 4,
      "run/replay/parity/offline_materialization": 4,
      "run/proofs": 14400,
      "run/audits": 5
    }
  },
  {
    "date": "2026-05-01",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 180037,
    "surface_counts": {
      "feed_snapshot": 4464,
      "unknown": 101948,
      "provider_runtime": 3269,
      "dhan_context": 580,
      "dataset_manifest": 27061,
      "family_surfaces": 20703,
      "execution_shadow": 2996,
      "redis_stream": 2306,
      "risk": 5716,
      "features": 12264,
      "strategy": 18581,
      "orders_no_order": 716,
      "option_ticks": 1500,
      "futures_ticks": 9
    },
    "roots": {
      "run/live_capture": 1,
      "run/evidence_bundles": 74514,
      "run/replay/parity": 213,
      "run/replay/parity/offline_materialization": 158,
      "run/proofs": 105137,
      "run/audits": 14
    }
  },
  {
    "date": "2026-05-02",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 72883,
    "surface_counts": {
      "unknown": 35254,
      "dataset_manifest": 9357,
      "risk": 2238,
      "execution_shadow": 1578,
      "features": 5843,
      "strategy": 9033,
      "feed_snapshot": 1938,
      "provider_runtime": 2301,
      "dhan_context": 272,
      "family_surfaces": 16980,
      "redis_stream": 1203,
      "orders_no_order": 241,
      "option_ticks": 489,
      "futures_ticks": 4
    },
    "roots": {
      "run/evidence_bundles": 70459,
      "run/replay/parity": 432,
      "run/replay/parity/offline_materialization": 412,
      "run/proofs": 1571,
      "run/audits": 9
    }
  },
  {
    "date": "2026-05-03",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 3827,
    "surface_counts": {
      "dataset_manifest": 196,
      "unknown": 2010,
      "family_surfaces": 411,
      "risk": 233,
      "features": 549,
      "execution_shadow": 307,
      "orders_no_order": 290,
      "strategy": 199,
      "provider_runtime": 107,
      "feed_snapshot": 28,
      "dhan_context": 10,
      "redis_stream": 32,
      "option_ticks": 4,
      "futures_ticks": 8
    },
    "roots": {
      "run/evidence_bundles": 2586,
      "run/replay/parity": 285,
      "run/replay/parity/offline_materialization": 285,
      "run/proofs": 664,
      "run/audits": 7
    }
  },
  {
    "date": "2026-05-04",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 4104,
    "surface_counts": {
      "features": 350,
      "feed_snapshot": 145,
      "strategy": 223,
      "unknown": 2782,
      "redis_stream": 97,
      "family_surfaces": 224,
      "dataset_manifest": 43,
      "risk": 90,
      "execution_shadow": 201,
      "provider_runtime": 205,
      "dhan_context": 20,
      "orders_no_order": 81,
      "option_ticks": 16,
      "futures_ticks": 1
    },
    "roots": {
      "run/live_capture": 21,
      "run/evidence_bundles": 3916,
      "run/proofs": 163,
      "run/audits": 4
    }
  },
  {
    "date": "2026-05-06",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 2193,
    "surface_counts": {
      "features": 196,
      "feed_snapshot": 85,
      "strategy": 97,
      "unknown": 1474,
      "orders_no_order": 40,
      "risk": 44,
      "execution_shadow": 100,
      "redis_stream": 53,
      "family_surfaces": 103,
      "dataset_manifest": 45,
      "provider_runtime": 117,
      "dhan_context": 10,
      "option_ticks": 24,
      "futures_ticks": 2
    },
    "roots": {
      "run/live_capture": 38,
      "run/evidence_bundles": 2069,
      "run/proofs": 82,
      "run/audits": 4
    }
  },
  {
    "date": "2026-05-08",
    "ingestion_candidate_score": 200,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 2865,
    "surface_counts": {
      "feed_snapshot": 96,
      "strategy": 116,
      "features": 226,
      "unknown": 1989,
      "dataset_manifest": 56,
      "redis_stream": 63,
      "family_surfaces": 145,
      "risk": 53,
      "execution_shadow": 146,
      "provider_runtime": 112,
      "dhan_context": 9,
      "orders_no_order": 38,
      "option_ticks": 24,
      "futures_ticks": 6
    },
    "roots": {
      "run/live_capture": 210,
      "run/evidence_bundles": 2197,
      "run/replay/parity": 26,
      "run/replay/parity/offline_materialization": 26,
      "run/proofs": 278,
      "run/audits": 128
    }
  },
  {
    "date": "2000-00-00",
    "ingestion_candidate_score": 190,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 4078,
    "surface_counts": {
      "unknown": 2800,
      "features": 400,
      "family_surfaces": 368,
      "feed_snapshot": 152,
      "risk": 228,
      "strategy": 194,
      "execution_shadow": 37,
      "redis_stream": 168,
      "provider_runtime": 7,
      "option_ticks": 9,
      "futures_ticks": 8,
      "dataset_manifest": 6,
      "orders_no_order": 4
    },
    "roots": {
      "run/live_capture": 6,
      "run/evidence_bundles": 1408,
      "run/replay/parity": 21,
      "run/replay/parity/offline_materialization": 18,
      "run/proofs": 2618,
      "run/audits": 7
    }
  },
  {
    "date": "2026-04-26",
    "ingestion_candidate_score": 190,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 8317,
    "surface_counts": {
      "unknown": 5641,
      "family_surfaces": 1239,
      "provider_runtime": 546,
      "redis_stream": 86,
      "dataset_manifest": 87,
      "features": 211,
      "feed_snapshot": 95,
      "strategy": 685,
      "risk": 94,
      "execution_shadow": 97,
      "dhan_context": 91,
      "orders_no_order": 1,
      "option_ticks": 2
    },
    "roots": {
      "run/live_capture": 1,
      "run/evidence_bundles": 4057,
      "run/replay/parity": 5,
      "run/replay/parity/offline_materialization": 5,
      "run/proofs": 4243,
      "run/audits": 6
    }
  },
  {
    "date": "2026-04-30",
    "ingestion_candidate_score": 190,
    "candidate_classification": "HIGH_VALUE_REVIEW",
    "file_count": 16702,
    "surface_counts": {
      "feed_snapshot": 1935,
      "features": 912,
      "strategy": 1797,
      "unknown": 8131,
      "execution_shadow": 608,
      "family_surfaces": 1688,
      "redis_stream": 364,
      "dataset_manifest": 235,
      "orders_no_order": 309,
      "provider_runtime": 2005,
      "risk": 315,
      "option_ticks": 4,
      "dhan_context": 7
    },
    "roots": {
      "run/live_capture": 15,
      "run/evidence_bundles": 8574,
      "run/replay/parity": 67,
      "run/replay/parity/offline_materialization": 41,
      "run/proofs": 7997,
      "run/audits": 8
    }
  }
]

No replay execution.
No repository mutation.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Run R5AO guarded source-shape audit for top candidate dates; no repository mutation yet.
