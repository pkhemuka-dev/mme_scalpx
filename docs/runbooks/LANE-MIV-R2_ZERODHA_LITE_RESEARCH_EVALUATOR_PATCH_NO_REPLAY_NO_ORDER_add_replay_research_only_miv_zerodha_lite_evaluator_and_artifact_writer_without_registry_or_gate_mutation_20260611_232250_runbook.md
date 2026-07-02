# LANE-MIV-R2_ZERODHA_LITE_RESEARCH_EVALUATOR_PATCH_NO_REPLAY_NO_ORDER_add_replay_research_only_miv_zerodha_lite_evaluator_and_artifact_writer_without_registry_or_gate_mutation_20260611_232250 Runbook

R2 added:

- app/mme_scalpx/replay/miv_research_evaluator.py

The evaluator:
- imports MIV-R contract from strategy_family
- emits research-shadow-only MIV rows
- writes MIV-specific artifacts
- keeps broker send hard-blocked
- keeps real order false
- does not add MIV_R to production registries
- does not execute replay

Next safe step:
- R2B output shape audit.
