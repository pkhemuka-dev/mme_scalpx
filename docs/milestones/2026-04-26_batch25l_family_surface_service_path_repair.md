
## Corrective Patch 5 — Branch Surface Kind Normalization

Timestamp: 20260426_133131

Batch 25L reached real rich-surface validation. Builders were called successfully:

```text
family_branch_builder_used = 10
family_root_builder_used = 5
no_builder_fallback = true
no_exact_builder_exception = true
no_optional_call_first_typeerror = true
```

The only failed checks were branch rich-surface checks because builders returned generic `surface_kind` values:

```text
mist
misb
misc
misr
miso
```

while the service-path contract expects branch-specific values:

```text
mist_branch
misb_branch
misc_branch
misr_branch
miso_branch
```

Freeze-grade repair:

- normalized branch `surface_kind` at the service adapter seam
- preserved original builder value as `builder_surface_kind`
- kept `family_id`, `branch_id`, `side`, and `rich_surface=true`
- did not change eligibility, provider selection, strategy promotion, risk, execution, broker behavior, or Redis ownership

Proof artifacts rerun:

```text
run/proofs/proof_feed_snapshot_feature_adapter.json
run/proofs/proof_family_surface_service_path.json
```
