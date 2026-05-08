# RAW-AA17-R2 — Trade Lifecycle / PnL Authority Resolver

generated_at_utc: 2026-05-02T07:27:29.257383+00:00

## Verdict

PnL lifecycle reconstruction is **not authorized / not derivable** in this batch.

Existing evidence may contain observed `net_pnl_after_costs`, but complete entry/exit/qty/cost lifecycle authority is not proven.

## Field status

```json
{
  "costs": "UNAVAILABLE",
  "entry_price": "UNAVAILABLE",
  "entry_ts": "UNAVAILABLE",
  "exit_price": "UNAVAILABLE",
  "exit_reason": "UNAVAILABLE",
  "exit_ts": "UNAVAILABLE",
  "gross_pnl": "UNAVAILABLE",
  "net_pnl_after_costs": "OBSERVED_ONLY",
  "qty": "UNAVAILABLE"
}
```

## Hard rules

- No PnL reconstruction.
- No row mutation.
- No replay execution.
- No broker IO.
- No live Redis writes.
- No paper/live enablement.

## Outputs

- required contract: `etc/research_gate/raw_trade_lifecycle_pnl_required_surface_contract.json`
- declaration template: `etc/research_gate/raw_trade_lifecycle_pnl_declaration_template.json`
- resolver report: `run/research_gate/raw_aa17_r2_trade_lifecycle_pnl_authority_resolver_20260502_125729/raw_aa17_r2_trade_lifecycle_pnl_authority_resolver_report.json`
- field status: `run/research_gate/raw_aa17_r2_trade_lifecycle_pnl_authority_resolver_20260502_125729/raw_aa17_r2_trade_lifecycle_pnl_field_status.json`