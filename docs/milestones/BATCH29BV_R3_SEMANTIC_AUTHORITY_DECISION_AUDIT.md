# Batch 29BV-R3 — Semantic Authority Decision Audit

- Generated UTC: 2026-05-03T10:44:58.776280+00:00
- Verdict: PARTIAL_P1_SEMANTIC_DRIFT_REQUIRES_PATCH_DECISION
- P1 unresolved count: 2
- Code patch applied: false
- Broker calls executed: false
- Redis writes executed: false
- Services started: false
- paper_armed: BLOCKED
- real live: BLOCKED

## Decisions

- RUNTIME_AUTHORITY_SPLIT: INTENTIONAL_BUT_MUST_BE_FROZEN_IN_CONTRACT (P1)
- SELECTED_OPTION_TRADABILITY_TRUTH_PROVIDER: LIKELY_SEMANTIC_DRIFT_REQUIRES_PATCH_DECISION (P1)
- DHAN_FALLBACK_EXECUTION_POLICY_SPLIT: LIKELY_SEMANTIC_DRIFT_REQUIRES_PATCH_DECISION (P1)
- CONTROLLED_ENTRY_SAFETY_GUARD: SAFETY_GUARD_PRESENT_ENTRY_EXECUTION_BLOCKED (SAFETY_PASS)

## Next best move

Patch one authority surface at a time only after this audit: first provider_roles selected-option truth, then Dhan fallback execution policy, then freeze runtime YAML observational law. No paper/live enablement.
