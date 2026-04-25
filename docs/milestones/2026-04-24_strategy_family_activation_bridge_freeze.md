# MME ScalpX Milestone — Strategy Family Activation Bridge Freeze

Date: 2026-04-24

## File Written

- `app/mme_scalpx/services/strategy_family/activation.py`

## Proof File

- `bin/proof_strategy_family_activation_bridge.py`

## Purpose

Create the first safe activation bridge after:

- feature-family payload seam freeze
- `features.py` offline proof
- strategy HOLD-only consumer bridge proof
- strategy-family compatibility proof
- all five doctrine leaves
- package-level doctrine proof

## What This Bridge Does

The bridge:

- consumes StrategyFamilyConsumerView or mapping-compatible payloads
- invokes all five doctrine leaves:
  - MIST
  - MISB
  - MISC
  - MISR
  - MISO
- normalizes candidate / no-signal / blocked results
- ranks candidates deterministically
- returns HOLD by default
- supports dry-run observation
- supports paper-only candidate promotion only with explicit activation mode and explicit promotion flag

## Safety Boundaries

The bridge does not:

- read Redis
- write Redis
- publish decisions
- place orders
- call broker APIs
- mutate execution
- mutate risk
- mutate strategy state
- change `strategy.py`
- enable live trading

## Activation Modes

- `hold_only`: default, always HOLD even when candidates exist
- `dry_run`: observes selected candidate, still HOLD
- `paper_armed`: may promote candidate only when `allow_candidate_promotion=True`
- live orders remain disabled

## Proof Completed

- compile/import proof
- all five doctrine leaves consumed
- default HOLD proof
- dry-run HOLD proof
- paper promotion blocked without explicit flag
- paper promotion allowed only with explicit flag
- unsafe view remains HOLD
- object-style consumer-view compatibility proof
- PUT-side selected view proof
- ownership AST proof
- doctrine package still passes
- strategy service still imports as HOLD bridge

## Next Step

Patch `strategy.py` only to import/use this activation bridge in report-only/dry-run mode, while continuing to emit HOLD decisions until explicit activation is separately armed.
