# MIV-R v0.1 Contract Amendment — Strategy-Family Placement

## Decision

MIV-R may later become a formal strategy family. Therefore its contract/schema/constants belong inside:

app/mme_scalpx/services/strategy_family/miv_r_contract.py

## Critical distinction

Inside strategy_family source tree does NOT mean active production registration.

At v0.1 MIV-R must remain:

- dormant
- research-shadow-only
- replay-first
- not production-active
- not live/paper enabled
- not broker-send capable

## Forbidden at v0.1

MIV-R must not be added to active production registries:

- STRATEGY_FAMILY_IDS
- DOCTRINE_IDS
- REPLAY_FEATURE_FAMILIES
- REPLAY_STRATEGY_FAMILIES

unless a later formal promotion batch explicitly approves it.

## Reason

MIV-R should be future-promotable as a real strategy family, but today it is only a research family used to exercise:

- candidate audit
- risk-shadow
- execution-shadow
- internal order-intent ledger
- later shadow PnL

## Safety

Real broker send remains hard-blocked.
Live trading remains hard-blocked.
Paper trading remains hard-blocked.
Risk service start remains forbidden.
Execution service start remains forbidden.
