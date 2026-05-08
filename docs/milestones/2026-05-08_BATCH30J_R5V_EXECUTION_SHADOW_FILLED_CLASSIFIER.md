# Batch 30J-R5V — Execution-Shadow Filled Field Classifier

Verdict: `PASS_EXECUTION_SHADOW_FILLED_FIELD_NON_FILL`
Classification: `FILLED_FIELD_PRESENT_BUT_FALSE_ZERO_NO_BROKER_ORDER_SIDE_EFFECT`

Record counts:
{
  "features_rows": 4,
  "strategy_decisions": 4,
  "risk_outputs": 4,
  "execution_shadow_results": 4,
  "counts_aligned": true
}

Execution-shadow classification:
{
  "filled_values": {
    "False": 4
  },
  "fill_qty_values": {
    "0": 4
  },
  "fill_price_values": {
    "None": 4
  },
  "execution_reason_values": {
    "risk_block_or_non_entry": 4
  },
  "risk_action_values": {
    "HOLD": 4
  },
  "symbol_values": {
    "NIFTY_FUT": 2,
    "NIFTY_CE": 2
  },
  "true_filled_row_count": 0,
  "nonzero_fill_qty_row_count": 0,
  "nonzero_fill_price_row_count": 0,
  "broker_like_row_count": 0,
  "order_id_like_row_count": 0
}

No replay execution.
No patch.
No Redis deletion.
No Redis restart.
No broker/order path.
No risk/execution start.

Next:
Run replay/live parity surface audit against available live evidence surfaces; still no paper/live.
