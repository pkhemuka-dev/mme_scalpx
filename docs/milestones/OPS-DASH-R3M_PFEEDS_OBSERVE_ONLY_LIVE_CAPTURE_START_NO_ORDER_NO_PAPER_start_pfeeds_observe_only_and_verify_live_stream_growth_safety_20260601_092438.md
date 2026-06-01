# OPS-DASH-R3M_PFEEDS_OBSERVE_ONLY_LIVE_CAPTURE_START_NO_ORDER_NO_PAPER_start_pfeeds_observe_only_and_verify_live_stream_growth_safety_20260601_092438

classification: `BLOCKED_OPS_DASH_R3M_ZLOGIN_FAILED_NO_PFEEDS_START_NO_ORDER_NO_PAPER`

## Safety

- orders before/after: `0 -> 0`
- risk stream before/after: `0 -> 0`
- execution stream before/after: `0 -> 0`
- risk proc after: `0`
- execution proc after: `0`

## Live stream growth

- fut_zerodha: `397 -> 397`
- opt_selected_zerodha: `1489 -> 1489`
- features: `4476 -> 4476`
- decisions: `1682 -> 1682`
- errors: `10024 -> 10024`

## Runtime

- zlogin_rc: `127`
- pfeeds_rc: `NA`
- pfeedcheck_rc: `NA`
- feeds_proc: `0`

## Logs

- pfeeds log: `run/live_capture/OPS-DASH-R3M_PFEEDS_OBSERVE_ONLY_LIVE_CAPTURE_START_NO_ORDER_NO_PAPER_start_pfeeds_observe_only_and_verify_live_stream_growth_safety_20260601_092438_pfeeds.log`
- pfeedcheck log: `run/live_capture/OPS-DASH-R3M_PFEEDS_OBSERVE_ONLY_LIVE_CAPTURE_START_NO_ORDER_NO_PAPER_start_pfeeds_observe_only_and_verify_live_stream_growth_safety_20260601_092438_pfeedcheck.log`

## Next

If PASS, keep capture running and check with:

```bash
pfeedcheck
```

Still forbidden:
- risk start
- execution start
- paper/live
- broker orders
