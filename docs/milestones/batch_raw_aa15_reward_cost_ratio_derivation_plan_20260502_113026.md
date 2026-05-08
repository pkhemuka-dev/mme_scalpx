# Batch RAW-AA15 — Reward/Cost Ratio Derivation Plan

created_at_utc: 2026-05-02T06:00:26.102303+00:00
verdict: `RAW_AA15_REWARD_COST_RATIO_DERIVATION_PLAN_DEFERRED`
blockers: `['COSTS_FIELD_EMPTY', 'NO_ROWS_HAVE_REWARD_TICKS_AND_COSTS', 'AA14_PNL_NOT_RECONSTRUCTABLE_FROM_ENTRY_EXIT_QTY_COSTS']`
next: `RAW_AA15_R2_COST_MODEL_DECLARATION_OR_COST_FIELD_BACKFILL_REQUIRED`

Plan/proof only. Does not write reward_cost_ratio.
No replay. No broker IO. No Redis live write. No order sending. No paper/live enablement.

proof: `run/proofs/proof_raw_aa15_reward_cost_ratio_derivation_plan.json`
freeze: `run/proofs/proof_raw_aa15_freeze_final.json`
doc: `docs/research_gate/RAW_AA15_REWARD_COST_RATIO_DERIVATION_PLAN.md`
run_dir: `run/research_gate/raw_aa15_reward_cost_ratio_derivation_plan_20260502_113026`
