# MISLS R4B Shadow Logger Skeleton Contract

## New module

app/mme_scalpx/services/strategy_family/misls_shadow_logger.py

## Canonical output surface

```text
research.misls.events
```

## Rule

R4B is a helper module only. It is not wired into features, strategy, registry, activation, risk, execution, broker, paper, or Redis.

## Research file path helpers

- run/research/misls_r3/events_YYYYMMDD.jsonl
- run/research/misls_r3/candidates_YYYYMMDD.jsonl
- run/research/misls_r3/rejections_YYYYMMDD.jsonl
- run/research/misls_r3/forward_paths_YYYYMMDD.jsonl