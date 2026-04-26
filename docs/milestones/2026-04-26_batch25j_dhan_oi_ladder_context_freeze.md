
## Corrective Patch 2 — Strike-Selection Ladder Alias De-Dupe

Timestamp: 20260426_132137

The Batch 25J proof reached real runtime validation and failed only:

```text
strike_selection_reads_frozen_json = false
```

Observed proof values:

```text
feature_ladder_size = 4
strike_selection_ladder_size = 8
```

Root cause:

```text
strike_selection.py read option_chain_ladder_json and strike_ladder_json as additive sources.
```

Freeze-grade repair:

- `option_chain_ladder_json` remains canonical
- `strike_ladder_json` remains a compatibility alias
- alias ladders are no longer double-counted
- stable row de-duplication is applied by instrument / side / strike identity
- no provider selection, strategy promotion, risk, execution, or broker behavior changed

Proof artifact rerun:

```text
run/proofs/proof_dhan_oi_ladder_persistence.json
```
