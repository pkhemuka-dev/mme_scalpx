# Batch 25Q-C — Strategy Import-Time Constant Corrective

Date: 2026-04-26
Timestamp: 20260426_141843

## Objective

Repair Batch 25Q after the disabled order-intent adapter patch exposed an import-time `strategy.py` constant gap.

## Root Cause

`strategy.py` referenced:

```text
POSITION_EFFECT_NONE
```

during module import, but the name was not defined before first use.

## Files Patched

- `app/mme_scalpx/services/strategy.py`

## Files Re-verified

- `app/mme_scalpx/services/strategy_family/order_intent.py`
- `app/mme_scalpx/services/strategy_family/activation.py`
- `bin/proof_order_intent_adapter_disabled.py`

## Safety Preserved

This corrective patch does not:

- enable strategy promotion
- enable execution arming
- publish non-HOLD decisions
- place broker orders
- mutate risk
- mutate execution
- change provider failover behavior

`strategy.py` remains HOLD-only.

## Proof

Proof artifact:

```text
run/proofs/proof_order_intent_adapter_disabled.json
```

Required result:

```text
order_intent_adapter_disabled_ok = True
order_intent_preview_valid = True
execution_contract_fields_complete = True
observe_only_still_publishes_hold = True
non_hold_publication_guard_still_blocks = True
proof_secret_scan_ok = True
```

## Verdict

Batch 25Q is freeze-final after the proof above is green.
