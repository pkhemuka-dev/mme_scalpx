# 2026-04-25 — Batch 10 strategy HOLD bridge contract freeze-final

## Scope

Target file:

```text
app/mme_scalpx/services/strategy.py
```

## Freeze issues closed

- read_feature_bundle no longer masks malformed JSON/schema errors as empty hash.
- publish_decision now enforces strategy.py HOLD-only law before Redis XADD.
- payload_json and flat action/qty are validated before publication.
- incoming flat payload_json cannot override canonical encoded payload.
- activation bridge promotion is proven clamped to HOLD/report-only.
- publish_error now includes ts_event_ns.
- run_once is proven to publish exactly one HOLD decision with qty 0.

## Proof artifact

```text
run/proofs/strategy_hold_bridge_contract.json
```

## Batch status

```text
Batch 10 strategy.py HOLD bridge contract: FREEZE-FINAL after proof output PASS
```

## Whole-project status

```text
NOT YET WHOLE-PROJECT FREEZE-FINAL
```

Remaining outside this batch:

- promoted StrategyOrderIntent / execution-native payload contract
- execution family entry safety proof
- risk exit-never-blocked proof
- Dhan full MISO-grade context materializer if not already separately patched
- replay/dataset.py blocker if still present
- longer live report-only observation
