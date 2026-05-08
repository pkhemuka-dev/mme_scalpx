# Batch 30J-R4F-R1 — Guarded Offline Runtime Isolation Cleanup

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: OFFLINE_RUNTIME_ISOLATION_CLEANUP_FAILED_OR_NOT_SAFE

Cleanup performed: True

Cleanup actions: [
  {
    "pid": 19233,
    "reason": "Lane C offline isolation: stop feeds runtime owner before metadata/replay trace continuation",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "alive_after_term": true,
    "alive_after_final": true,
    "ok": false
  },
  {
    "pid": 19238,
    "reason": "Lane C offline isolation: stop features runtime owner before metadata/replay trace continuation",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "alive_after_term": true,
    "alive_after_final": true,
    "ok": false
  },
  {
    "pid": 19243,
    "reason": "Lane C offline isolation: stop strategy runtime owner before metadata/replay trace continuation",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "alive_after_term": true,
    "alive_after_final": true,
    "ok": false
  }
]

Blockers: [
  "ALL_CLEANUP_ACTIONS_OK_BLOCKER"
]

Review: [
  "FEATURES_STREAM_MOVED_DURING_CLEANUP_REVIEW",
  "DECISIONS_STREAM_MOVED_DURING_CLEANUP_REVIEW",
  "ERRORS_STREAM_MOVED_DURING_CLEANUP_REVIEW"
]

Next: Do not install metadata or run replay. Inspect 30J-R4F-R1 cleanup blockers first.

Safety: no replay execution, no selector metadata install, no Redis key/lock deletion, no Redis restart, no paper/live, no orders. Only guarded SIGTERM of app.mme_scalpx.main runtime owners if eligible.
