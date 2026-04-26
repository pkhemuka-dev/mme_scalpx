# Batch 25I — Feed Snapshot to Feature Raw-Surface Adapter

Date: 2026-04-26
Timestamp: 20260426_131615

## Objective

Repair `features.py` so it can consume the feed-shaped hashes written by `feeds.py`.

## Dependency

Batch 25H provider runtime seam proof passed before this batch:

```text
run/proofs/proof_provider_runtime_contract_seam.json
provider_runtime_contract_seam_ok = true
```

## Files Patched

- `app/mme_scalpx/services/features.py`
- `bin/proof_feed_snapshot_feature_adapter.py`

## Frozen Input Shape

The adapter now recognizes:

```text
future_json
selected_call_json
selected_put_json
ce_atm_json
ce_atm1_json
pe_atm_json
pe_atm1_json
bid_qty_5
ask_qty_5
```

## Frozen Output Requirements

Proof requires:

```text
futures.present = true
futures.depth_total = bid_qty_5 + ask_qty_5
CALL selected option present from selected_call_json
PUT selected option present from selected_put_json
instrument_key preserved
instrument_token preserved
option_symbol / trading_symbol preserved
strike preserved
tradability_ok true for valid premium/spread/depth
```

## Proof

Proof artifact:

```text
run/proofs/proof_feed_snapshot_feature_adapter.json
```

Required result:

```text
feed_snapshot_feature_adapter_ok = true
```

## Runtime Safety

This batch does not:

- enable strategy promotion
- arm execution
- change risk
- change provider selection
- change failover policy
- introduce broker credentials into proof artifacts

`observe_only` remains default.

## Remaining Outside This Batch

- Batch 25J: Dhan OI ladder / option-chain context persistence
- Batch 25K: shared feature-family builder ABI repair
- Batch 25L: family branch/root surface wiring repair
- Batch 25M: canonical family support alias and eligibility repair
- Batch 25N: MISO provider doctrine alignment

## Verdict

Batch 25I is freeze-final only if:

```json
"feed_snapshot_feature_adapter_ok": true
```

appears in:

```text
run/proofs/proof_feed_snapshot_feature_adapter.json
```
