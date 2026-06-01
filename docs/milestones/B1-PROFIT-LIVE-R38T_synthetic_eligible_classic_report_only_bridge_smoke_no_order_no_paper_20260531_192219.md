# B1-PROFIT-LIVE-R38T_synthetic_eligible_classic_report_only_bridge_smoke_no_order_no_paper_20260531_192219

## Verdict
`PASS_R38T_SYNTHETIC_CLASSIC_REPORT_ONLY_BRIDGE_SMOKE_NO_ORDER`

## Meaning
R38T proves the synthetic classic eligible candidate bridge in report-only mode. No patch was applied in this batch.

## Safety
- orders: `0`
- risk_stream: `0`
- execution_stream: `0`
- lock_execution: ``
- pauto_stopped: `True`
- pseal_pass: `True`
- no_live_processes: `True`

## Key smoke checks
- bridge_smoke_pass: `True`
- classic env allows paper_armed marker: `True`
- MISO env blocks: `True`
- broker env blocks: `True`
- scope selector classic smoke ok: `True`
- bad scope does not select MISO: `True`
- live_orders false in candidate: `True`

## Rule
No paper/risk/execution/order was started.


# B1-PROFIT-LIVE-R38T_synthetic_eligible_classic_report_only_bridge_smoke_no_order_no_paper_20260531_192219 runbook

## Next
R38U should validate the controlled-paper route/order-cycle request builder as a dry-run data object only.

Rules:
- no risk start
- no execution start
- no order
- no broker call
- no Redis delete
- keep Zerodha-only / 1-lot / classic-only / MISO-blocked law
