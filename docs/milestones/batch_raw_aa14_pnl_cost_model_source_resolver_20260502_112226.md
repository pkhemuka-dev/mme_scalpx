# Batch RAW-AA14 — PnL Cost Model Source Resolver

created_at_utc: 2026-05-02T05:52:26.594579+00:00
verdict: `RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER_READY`
blockers: `[]`
next: `RAW_AA15_REWARD_COST_RATIO_DERIVATION_PLAN`

Profiles PnL/cost source fields from AA13B-R4 derived row-level output.
Does not derive reward_cost_ratio yet.
No replay. No broker IO. No Redis live write. No order sending. No paper/live enablement.

proof: `run/proofs/proof_raw_aa14_pnl_cost_model_source_resolver.json`
freeze: `run/proofs/proof_raw_aa14_freeze_final.json`
doc: `docs/research_gate/RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER.md`
run_dir: `run/research_gate/raw_aa14_pnl_cost_model_source_resolver_20260502_112226`
