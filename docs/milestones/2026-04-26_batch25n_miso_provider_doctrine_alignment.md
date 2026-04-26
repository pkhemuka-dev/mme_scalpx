
## Corrective Patch 2 — MISO YAML Futures Policy Literal

Timestamp: 20260426_134044

The Batch 25N proof reached real doctrine/runtime validation. Provider-gate cases passed, but config alignment failed:

```text
miso_yaml_alignment_ok = false
```

Root cause:

```text
miso_call.yaml and miso_put.yaml described the futures policy structurally but did not contain the frozen literal:
ZERODHA_OR_DHAN_HEALTHY_SYNCED
```

Freeze-grade repair:

- patched only `etc/strategy_family/frozen/miso_call.yaml`
- patched only `etc/strategy_family/frozen/miso_put.yaml`
- added `futures_policy: ZERODHA_OR_DHAN_HEALTHY_SYNCED`
- did not change provider gate logic, doctrine_contracts.py, miso.py, strategy promotion, risk, execution, broker behavior, or Redis ownership

Proof artifact rerun:

```text
run/proofs/proof_miso_provider_doctrine_alignment.json
```
