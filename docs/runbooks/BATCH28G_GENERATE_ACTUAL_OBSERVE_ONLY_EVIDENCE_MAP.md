Batch 28G Generate actual observe_only evidence map from market-session proof outputs

Date: 2026-05-01

Purpose:
Generate the candidate and, only when complete, final observe_only actual evidence map required by Batch 28F.

Safety:
28G does not start services.
28G does not read live Redis.
28G does not write live Redis.
28G does not call broker APIs.
28G does not approve paper_armed.
28G does not approve live trading.
28G does not prove full replay/live parity.

Final evidence map path:
etc/replay/parity/observe_only_actual_generated_evidence_map.json

Candidate evidence map path:
etc/replay/parity/observe_only_actual_generated_evidence_map_candidate_28g.json

Missing report:
run/proofs/observe_only_actual_evidence_map_missing_report_28g.json

If proof outputs are missing:
28G closes as DEFERRED_MARKET_SESSION_PROOF_OUTPUTS_REQUIRED_28G and does not publish the final map.

If all proof outputs exist:
28G publishes the final evidence map and next you may rerun Batch 28F to collect the package.
