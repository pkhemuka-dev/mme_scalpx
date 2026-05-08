Batch 28F Real observe_only market-session package collection from actual generated evidence map

Date: 2026-05-01

Verdict: DEFERRED_ACTUAL_EVIDENCE_MAP_REQUIRED_28F

Accepted for: DEFERRED_ACTUAL_EVIDENCE_MAP_REQUIRED

Scope:
28F installs and proves the actual evidence-map package collection path.
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

Actual package collected:
False

Deferred:
True

If deferred:
Market-session evidence map is not present yet. Generate actual observe_only market-session evidence first, then rerun 28F with OBSERVE_ONLY_EVIDENCE_MAP pointing to the generated map.

Proofs:
run/proofs/proof_observe_only_actual_evidence_map_collection_contract.json
run/proofs/proof_observe_only_actual_evidence_map_collection_no_enablement.json
run/proofs/proof_observe_only_market_session_package_collection_28f.json
run/proofs/proof_observe_only_market_session_package_collection_28f_latest.json

Next:
If 28F is deferred, generate actual observe_only market-session evidence map first.
If 28F collected actual package, proceed to Batch 28G replay/live parity comparison using collected package, still not paper/live enablement.
