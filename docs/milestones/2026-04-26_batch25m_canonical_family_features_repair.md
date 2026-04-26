
## Corrective Patch 2 — MISC Alias Fixture + MISR Branch-Strict Active Zone

Timestamp: 20260426_133343

The Batch 25M proof reached real canonical-support validation and failed only:

```text
MISC_canonical_aliases_mapped = false
MISR_expected_call_branch_only = false
```

Root causes:

- MISC proof fixture did not include `hesitation_ok`, so `hesitation_valid` could not map true.
- MISR root-level `active_zone_valid` leaked into the inactive sibling branch.

Freeze-grade repair:

- added `hesitation_ok` to the MISC synthetic true setup fixture
- made MISR `active_zone_valid` branch-strict
- inactive MISR sibling branches no longer receive root active-zone truth unless they also carry branch-local setup signals
- did not change provider selection, strategy promotion, risk, execution, broker behavior, or Redis ownership

Proof artifact rerun:

```text
run/proofs/proof_family_features_canonical_support.json
```
