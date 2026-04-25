# 2026-04-25 — Batch 1 strategy-family leaf candidate contract freeze-final

## Scope

Target files:

```text
app/mme_scalpx/services/strategy_family/mist.py
app/mme_scalpx/services/strategy_family/misb.py
app/mme_scalpx/services/strategy_family/misc.py
app/mme_scalpx/services/strategy_family/misr.py
app/mme_scalpx/services/strategy_family/miso.py
```

## Freeze issues closed

- Missing classic runtime mode now fails closed to DISABLED.
- Missing/unknown MISO mode now fails closed to DISABLED.
- Candidate post-evaluation guard added to all five doctrine leaves.
- Candidate family/doctrine/branch/action invariants are enforced.
- Candidate score/priority bounds are enforced.
- Candidate order metadata completeness is enforced:
  - instrument_key
  - instrument_token or option_symbol
  - strike
  - positive option_price
  - positive tick_size
- 5-point target and 4-point stop contract are enforced.
- get_evaluator remains compatible with the current evaluate wrapper.
- No Redis, broker, execution, risk, or cooldown ownership was added.

## Proof artifact

```text
run/proofs/strategy_family_leaf_candidate_contract.json
```

## Batch status

```text
Batch 1 strategy-family leaf candidate contract: FREEZE-FINAL after proof output PASS
```

## Whole-project status

```text
NOT YET WHOLE-PROJECT FREEZE-FINAL
```

Remaining outside this batch:

- promoted StrategyOrderIntent / execution-native payload builder
- execution family entry safety proof
- risk exit-never-blocked proof
- Dhan full MISO-grade context materializer if not already separately patched
- replay/dataset.py blocker if still present
- longer live report-only observation
