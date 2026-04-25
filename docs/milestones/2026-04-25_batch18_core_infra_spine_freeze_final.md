# 2026-04-25 — Batch 18 core infrastructure spine freeze-final

## Scope

```text
app/mme_scalpx/core/settings.py
app/mme_scalpx/core/redisx.py
app/mme_scalpx/core/codec.py
app/mme_scalpx/core/clock.py
```

## Freeze issues closed

- codec.py resolves postponed dataclass annotations in hash/event helper paths.
- codec.py exposes decode_model_from_envelope_as(model_cls, envelope).
- redisx.py typed stream helper seam uses strict typed envelope decode.
- settings.py exposes runtime-truth introspection without changing runtime behavior.
- clock.py behavior remains unchanged; the proof records that late-entry cutoff is not owned by core clock.
- Aggregate Batch 18 proof artifact is written and verified.

## Proof artifact

```text
run/proofs/core_infra_batch18_freeze.json
```

## Batch status

```text
Batch 18 core infrastructure spine: FREEZE-FINAL after proof output PASS
```

## Whole-project status

```text
NOT YET WHOLE-PROJECT FREEZE-FINAL
```

Remaining outside this batch:

- final effective runtime source-of-truth decision: settings/env vs runtime.yaml/systemd/main
- promoted StrategyOrderIntent / execution-native payload builder if not separately completed
- execution family entry safety proof if not separately completed
- longer live report-only observation
- config registry classification / zero-byte strategy-family YAML quarantine if not separately completed
