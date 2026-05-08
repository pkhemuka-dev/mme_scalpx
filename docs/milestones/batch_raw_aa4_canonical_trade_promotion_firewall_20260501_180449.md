# RAW-AA4 Canonical Trade Promotion Firewall

created_at_utc: 2026-05-01T12:34:49.359287+00:00

## Verdict

- firewall_verdict: `RAW_AA4_PROMOTION_FIREWALL_REJECTED`
- promotion_recommendation: `DO_NOT_PROMOTE_SAMPLE_OR_CONTEXT_INSUFFICIENT`
- raw_aa4_freeze_final_ok: `True`
- validation_only: `true`
- patching_performed: `false`

## Evidence

- trade_count: `88`
- family_trade_counts: `{'MIST': 72, 'MISB': 4, 'MISC': 4, 'MISR': 4, 'MISO': 4}`
- unknown_family_ratio: `0.0`
- net_pnl_total: `9123.0`
- win_rate: `0.6818181818181818`
- oi_wall_coverage: `0.022727272727272728`

## Blocking reasons

`['sample_size_ok', 'family_balance_ok', 'oi_wall_coverage_ok']`

No live runtime, broker IO, Redis live writes, order sending, strategy/risk/execution mutation, or paper/live enablement.
