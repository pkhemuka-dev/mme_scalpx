# LANE-X-R32F-R1_COMPACT_AUDIT_R32E_RISK_REJECTIONS_NO_PATCH_NO_REPLAY_NO_ORDER_compact_inspect_r32e_internal_ledgers_rejection_reasons_20260611_230525

classification: PASS_R32F_R1_REAL_CANDIDATE_RISK_REJECTION_AUDITED_NO_PATCH_NO_REPLAY_NO_ORDER

## Result

- source_candidate_count: `20`
- candidate_intent_count: `20`
- risk_row_count: `20`
- execution_row_count: `20`
- order_row_count: `20`

## Risk rejection reasons

```json
{
  "unsupported_action_for_internal_entry": 20
}
```

## Side counts

```json
{
  "CALL": 13,
  "PUT": 7
}
```

## Action counts

```json
{
  "HOLD": 20
}
```

## Symbol presence

```json
{
  "present": 20
}
```

## Next decision

`PATCH_R32G_REAL_CANDIDATE_NORMALIZER_FOR_R9X_SHAPE`

## Safety

- orders: `0`
- risk: `0`
- execution: `0`

## Boundary

- no patch
- no replay
- no broker order
- no Redis delete
- no lock delete
