
## Corrective Patch 2 — MISC Retest Monitor Consumer

Timestamp: 20260426_134332

The Batch 25O reverse coverage proof reached real validation and failed only for:

```text
MISC CALL retest_monitor_active
MISC PUT retest_monitor_active
```

Root cause:

```text
feature_family and features.py produced/canonicalized retest_monitor_active,
but strategy_family/misc.py did not consume the canonical key or accepted aliases.
```

Freeze-grade repair:

- patched only `app/mme_scalpx/services/strategy_family/misc.py`
- added explicit non-promotional consumer read for:
  - `retest_monitor_active`
  - `retest_monitor_alive`
  - `retest_monitor`
- preserved the frozen MISC evaluator by delegating to the original `evaluate_branch`
- did not change candidate promotion, risk, execution, broker behavior, provider behavior, or Redis ownership

Proof artifact rerun:

```text
run/proofs/proof_strategy_family_reverse_coverage.json
```
