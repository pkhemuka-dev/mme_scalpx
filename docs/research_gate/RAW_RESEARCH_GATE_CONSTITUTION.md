# RAW-B — RAW / Research Gate Constitution Freeze

Date: 2026-05-01
Generated UTC: 2026-05-01T07:09:52.894711+00:00
Batch tag: batch_raw_a_b_freeze_final_v2_20260501_123952

## Identity

RAW means Research & Analysis Wing.

RAW / Research Gate is the permanent non-live research and analysis wing of MME-ScalpX.

Its purpose is to convert broker-aware recorded data, replay outputs, family surfaces, Dhan/OI context, strategy decisions, blocker chains, and execution outcomes into auditable evidence for improving MIST, MISB, MISC, MISR, and MISO.

## Core freeze laws

1. RAW creates evidence only.
2. RAW does not trade.
3. RAW does not mutate production.
4. RAW does not duplicate raw capture.
5. RAW does not write live Redis truth.
6. RAW does not own risk.
7. RAW does not own execution.
8. RAW does not own broker IO.
9. RAW does not own position truth.
10. RAW does not enable paper/live.
11. RAW does not bypass replay, paper, or live governance.
12. RAW reads existing archive, replay, proof, live-capture, family-surface, Dhan/OI, decision, risk, and execution artifacts.
13. RAW writes compact research reports only.
14. RAW may recommend shadow tests, paper proposals, or production patch proposals, but never directly enables them.

## Required separation

RAW must maintain two separate evidence tracks.

### Track 1: Live evidence audit

Purpose:

- prove the real system ran safely
- prove data was captured cleanly
- prove provider/OI/family surfaces existed
- prove no forbidden order path occurred
- prove live runtime did not mutate because of RAW

Outputs later:

- live_dataset_quality_report.json
- live_provider_context_report.json
- live_family_surface_report.json
- live_safety_report.json

### Track 2: Replay evidence audit

Purpose:

- calculate replay/backtest PnL
- compare strategies
- compare baseline vs shadow
- test OI-wall impact
- detect missed trades
- detect false entries
- rank strategy/family/side/regime performance

Outputs later:

- replay_backtest_verdict.json
- pnl_report.json
- strategy_rank_report.json
- oi_wall_impact_report.json
- missed_trade_report.json
- false_entry_report.json

### Track 3: Live-vs-replay parity

Purpose:

- check whether replay used comparable surfaces to live
- check whether live capture is good enough for replay
- explain mismatch between replay and live/paper outcomes

Outputs later:

- live_replay_parity_report.json
- replay_data_readiness_report.json

## Correct architecture

broker feeds and live services
  -> research_capture
  -> archive, manifests, integrity reports
  -> replay, backtest, shadow experiments
  -> RAW / research_gate
  -> evidence verdict and improvement proposal
  -> manual patch, proof, and freeze governance

## RAW owns

- dataset quality verdicts
- replay/backtest verdicts
- PnL analysis
- strategy ranking
- family/side/regime matrix
- OI-wall impact analysis
- strike-selection impact analysis
- candidate/blocker audit
- missed-trade audit
- false-entry audit
- market-condition analysis
- baseline-vs-shadow comparison
- promotion-readiness reports
- future ML-ready labels
- system drift analytics

## RAW does not own

- live entries
- live exits
- order placement
- broker order truth
- fill truth
- position truth
- risk veto
- execution routing
- live Redis truth
- strategy doctrine mutation
- paper/live enablement

## OI-wall law

OI wall is research, context, strike-quality, and slow-evidence surface.

OI wall must not silently become immediate trigger truth.

For option-led logic, chain OI, IV, delta, and option-chain context remain slow-context selection evidence. Sub-second trigger truth must remain with the live selected option feed, shadow-strike live feed where applicable, and futures alignment/veto surfaces.

## Replay/PnL verdict law

RAW replay verdicts must be richer than PASS/FAIL.

Allowed research verdicts:

- PASS_WITH_POSITIVE_EDGE
- PASS_BUT_LOW_SAMPLE
- PASS_BUT_HIGH_DRAWDOWN
- PASS_ONLY_IN_ONE_REGIME
- REJECT_NEGATIVE_EXPECTANCY
- REJECT_OVERFIT_RISK
- INCONCLUSIVE_DATA_INSUFFICIENT
- READY_FOR_SHADOW_PAPER_PROPOSAL
- READY_FOR_PAPER_TEST_PROPOSAL
- PRODUCTION_PATCH_PROPOSAL_ONLY

Forbidden RAW verdicts:

- ENABLE_LIVE
- ENABLE_PAPER_ARMED
- SEND_ORDER
- MUTATE_CONFIG_NOW
- OVERRIDE_RISK
- OVERRIDE_EXECUTION

## RAW-B verdict

PASS.

This constitution freezes RAW as a non-live evidence and governance layer.
