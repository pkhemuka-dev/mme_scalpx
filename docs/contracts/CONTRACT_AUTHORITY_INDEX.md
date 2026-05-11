# MME-ScalpX Contract Authority Index

This file freezes the authority order for future audits, patches, generated command packages, and AI-assisted changes.

## Authority Order

1. Latest uploaded evidence/proof bundle
2. Current filesystem inspection
3. Frozen contract file
4. Milestone summary
5. Memory/chat summary
6. Assumption

Assumptions are never authoritative.

## 1. Core Spine Authority

Primary path: app/mme_scalpx/core/

Authoritative files:
- names.py
- models.py
- codec.py
- redisx.py
- clock.py
- settings.py
- validators.py

Rules:
- names.py owns names and constants only.
- models.py owns schemas and validation surfaces.
- codec.py owns serialization/deserialization.
- redisx.py owns Redis transport helpers.
- clock.py owns time/session primitives.
- settings.py owns configuration loading.
- validators.py owns primitive validators.
- Core spine must not contain strategy, broker, paper/live enablement, or replay execution logic.

## 2. Runtime Safety Authority

Primary files:
- app/mme_scalpx/services/risk.py
- app/mme_scalpx/services/execution.py
- app/mme_scalpx/services/controlled_paper_runtime.py
- app/mme_scalpx/integrations/broker_api.py
- app/mme_scalpx/integrations/dhan_execution.py

Rules:
- Execution is sole order/position truth.
- Risk may block entries but must not block mandatory exits.
- Broker calls must remain explicitly gated.
- Real live trading is forbidden unless separately approved by contract.
- Controlled paper requires explicit scope, quantity, provider, flat-position, session/time, and route gates.

## 3. Strategy Family Authority

Primary paths:
- app/mme_scalpx/services/feature_family/
- app/mme_scalpx/services/strategy_family/
- config/strategy_family/

Families:
- MIST
- MISB
- MISC
- MISR
- MISO

Rules:
- Required stage flags must fail closed when missing or false.
- Missing provider readiness must not silently become eligible.
- Candidate generation is not order permission.

## 4. Replay Authority

Primary path: app/mme_scalpx/replay/

Rules:
- Replay is offline-safe by default.
- Replay must not call brokers.
- Replay must not write live Redis trading truth.
- Replay contracts freeze schema before writer/runtime changes.

## 5. Replay Optimization / ML Authority

Primary path: app/mme_scalpx/replay_optimization/

Rules:
- Optimization candidates are advisory until bound to verified result packs.
- Label binding requires verified candidate-specific result packs.
- ML outputs must not become production truth without promotion evidence.

## 6. Research Capture Authority

Primary path: app/mme_scalpx/research_capture/

Rules:
- Research capture archives and normalizes evidence.
- Research capture must not mutate runtime truth.
- Research capture must not enable paper/live.

## 7. Research Gate / RAW Authority

Primary path: app/mme_scalpx/research_gate/

Rules:
- Research gate is analytical and non-live.
- PnL, ranking, OI wall, promotion, and replay verdict outputs are advisory until ratified.
- Research gate must not send orders.

## 8. Controlled Paper Authority

Primary paths:
- docs/contracts/*controlled_paper*
- app/mme_scalpx/services/controlled_paper_runtime.py
- app/mme_scalpx/services/risk.py
- app/mme_scalpx/services/execution.py

Rules:
- Explicit scope only.
- One family/side/scope at a time unless separately approved.
- One lot only unless separately approved.
- Paper/sandbox only.
- Real live forbidden.
- No broker failover.
- No mid-position provider migration.

## 9. AI Patch Runner Authority

Primary path: ai_patch_runner/

Rules:
- Policy and safety files define generated patch boundaries.
- Generated outputs are evidence artifacts, not source truth.
- AI patches must go through sandbox/review bundle flow before application.
