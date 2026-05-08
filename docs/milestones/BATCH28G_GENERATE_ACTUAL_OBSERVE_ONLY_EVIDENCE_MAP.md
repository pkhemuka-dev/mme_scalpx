Batch 28G Generate actual observe_only evidence map from market-session proof outputs

Date: 2026-05-01

Verdict: DEFERRED_MARKET_SESSION_PROOF_OUTPUTS_REQUIRED_28G

Accepted for: DEFERRED_MARKET_SESSION_PROOF_OUTPUTS_REQUIRED

Scope:
28G generates a candidate observe_only evidence map from market-session proof outputs.
28G publishes the final evidence map only when all required real proof outputs exist.
28G does not start services.
28G does not read live Redis.
28G does not write live Redis.
28G does not call broker APIs.
28G does not approve paper_armed.
28G does not approve live trading.
28G does not prove full replay/live parity.

Candidate map:
etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json

Final map:
etc/replay/parity/observe_only_actual_generated_evidence_map.json

Missing report:
run/proofs/observe_only_actual_evidence_map_missing_report_28g.json

Final map published:
False

Found count:
7

Missing count:
5

If deferred:
Generate actual market-session proof outputs first, then rerun Batch 28G.
Do not manually create fake final evidence maps.

If passed:
Rerun Batch 28F to collect the actual package from the generated final map.

Proofs:
run/proofs/proof_observe_only_actual_evidence_map_generation_contract.json
run/proofs/proof_observe_only_actual_evidence_map_generation_no_enablement.json
run/proofs/proof_observe_only_actual_evidence_map_generation_28g.json
run/proofs/proof_observe_only_actual_evidence_map_generation_28g_latest.json

Next:
If deferred, run actual observe_only market-session proof generation first.
If generated, rerun Batch 28F.
