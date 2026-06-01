# B1-PROFIT-LIVE-R38ZD_selected_option_timestamp_clock_domain_audit_no_patch_no_order_no_paper_20260531_213446 runbook

## Next
R38ZE should patch:
`features.py R38ZB timestamp resolver should reject payload ts far from frame/stream and accept receive/stream clock when available`

Rules:
- reject payload timestamp if far from feature/futures clock
- prefer receive/stream clock only if actually available
- no risk/execution/order/broker
