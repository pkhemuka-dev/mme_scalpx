
## Corrective Patch 6 — Direct Behavior Architecture Probe

Timestamp: 20260426_140827

The real Batch 25R seam checks passed repeatedly:

```text
valid_promoted_entry_reaches_broker_with_risk_cap = true
risk_veto_blocks_entry = true
risk_zero_lots_blocks_entry = true
HOLD_ignored_by_execution = true
exit_not_blocked_by_risk = true
```

The only failed check was:

```text
risk_architecture_frozen_global_entry_gate = false
```

Root cause:

```text
The proof-local architecture probe still depended on source-token inspection.
```

Freeze-grade repair:

- patched only `bin/proof_risk_gate_execution_integration.py`
- architecture proof now depends on:
  - frozen risk-hash keys in the proof samples:
    - `veto_entries`
    - `max_new_lots`
    - `allow_exits`
  - observed dry-run seam behavior:
    - risk veto blocks entries
    - max_new_lots=0 blocks entries
    - entry veto does not block exits
- did not change `risk.py`
- did not change `execution.py`
- did not enable strategy promotion
- did not arm execution
- did not call real broker APIs
- did not change Redis ownership

Proof artifacts rerun:

```text
run/proofs/proof_execution_entry_contract_dryrun.json
run/proofs/proof_risk_gate_execution_integration.json
```
