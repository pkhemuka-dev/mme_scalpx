# LANE D2 D41-R2 — Lane E Candidate Materialization Intake Runbook

## Purpose

D2-D41 freezes the Lane E candidate materialization intake contract after Lane D D40 confirms Lane D replay optimization is complete and must hand off to Lane C/E.

This is no-execution.

## R2 Correction

D39 proof verdict and safety are validated directly. If D39 does not expose package_status as a top-level key, D39 package readiness is validated through the D40 freeze-summary D39 row.

## Required Predecessor Proofs

- run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json
- run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json
- run/proofs/proof_lane_d_d40_lane_d_freeze_summary_latest.json

All must be PASS.

## Required D1 Input

D2 does not select candidates.

When D1 provides the 5-candidate subset manifest, export:

export LANE_D1_SUBSET_MANIFEST="run/replay_optimization/<d1_subset_manifest>.json"

Required top-level fields:

- subset_manifest_id
- subset_created_at
- source_candidate_count
- selected_candidate_count
- selected_candidates

Required per-candidate fields:

- candidate_id
- candidate_fingerprint
- planned_result_pack_root

## Lane E Expected Future Outputs Per Candidate

- candidate_profile.json
- candidate_replay_manifest.json
- candidate_effective_inputs.json
- candidate_result_pack_manifest.json
- candidate_integrity_report.json
- candidate_result_context_catalog.json
- candidate_label_binding_precondition.json
- materialization_execution_manifest.json
- materialization_preflight_safety_report.json
- materialization_acceptance_report.json

## Safety Boundary

D2-D41 does not execute replay, create real result packs, bind labels, calculate PnL, train ML, call brokers, write live Redis, start runtime services, enable paper/live, patch replay runner, or claim profitability.

## Lane C Stop Rule

If Lane E materialization depends on replay runner behavior, bin/replay_run.py, staging compatibility, or a Lane C-owned seam, Lane E must stop and wait for current Lane C proof before execution.

## Next

LANE-D2-D42 — Lane E Subset Intake Validator / No Execution
