
## Corrective Patch 2 — provider_runtime_mode Optional Compatibility Field

Timestamp: 20260426_130654

The provider-runtime seam proof reached contract validation after the import-path fix, but failed with:

```text
provider_runtime.provider_runtime_mode must be non-empty str
```

Root cause:

```text
features.py emitted provider_runtime_mode="" for a compatibility field.
```

Freeze-grade repair:

- canonical runtime truth remains `family_runtime_mode`
- `provider_runtime_mode` is compatibility-only
- absent compatibility value is now emitted as `None`, not an empty string
- no provider selection, promotion, strategy behavior, execution behavior, or broker behavior changed

Proof artifact rerun:

```text
run/proofs/proof_provider_runtime_contract_seam.json
```
