Batch 28F Real observe_only market-session package collection from actual generated evidence map

Date: 2026-05-01

Purpose:
Install and prove the package-collection path for an actual generated observe_only market-session evidence map.

Scope:
28F does not start services.
28F does not read live Redis.
28F does not write live Redis.
28F does not call broker APIs.
28F does not approve paper_armed.
28F does not approve live trading.
28F does not prove full replay/live parity.

Actual evidence map:
etc/replay/parity/observe_only_actual_generated_evidence_map.json

Package root:
run/replay/parity/live_evidence/observe_only_actual_market_session

If the actual evidence map is missing:
Verdict is DEFERRED_ACTUAL_EVIDENCE_MAP_REQUIRED_28F.
This is not a failure; it means market-session evidence has not yet been generated.

Future actual collection command:
cd /home/Lenovo/scalpx/projects/mme_scalpx
OBSERVE_ONLY_CAPTURE_ID=observe_only_YYYYMMDD OBSERVE_ONLY_EVIDENCE_MAP=etc/replay/parity/observe_only_YYYYMMDD_evidence_map.json OBSERVE_ONLY_PACKAGE_ROOT=run/replay/parity/live_evidence/observe_only_YYYYMMDD .venv/bin/python /tmp/batch28f_actual_evidence_map_collection_freeze_final.py

Manual collector command:
.venv/bin/python bin/observe_only_market_session_package_collect.py --capture-id observe_only_YYYYMMDD --evidence-map etc/replay/parity/observe_only_YYYYMMDD_evidence_map.json --root run/replay/parity/live_evidence/observe_only_YYYYMMDD
