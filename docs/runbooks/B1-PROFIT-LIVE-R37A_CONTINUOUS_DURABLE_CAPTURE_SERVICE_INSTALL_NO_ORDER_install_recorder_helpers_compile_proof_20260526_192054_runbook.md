# B1-PROFIT-LIVE-R37A_CONTINUOUS_DURABLE_CAPTURE_SERVICE_INSTALL_NO_ORDER

## Purpose

Install a continuous durable Redis stream recorder for the next live session.

This fixes the two-day failure mode:

- Redis is only hot buffer, not durable storage.
- pseal at market close is too late for tick streams.
- Full-day backtest requires continuous append-to-disk during market.

## Installed file

`bin/b1_profit_live_durable_capture.py`

## Installed helpers

```bash
source ~/.bash_aliases
pcapture_start
pcapture_status
pcapture_stop
```

## Live-session use tomorrow

1. Start normal capture stack safely.
2. Confirm `pcheck` says recording OK.
3. Run:

```bash
source ~/.bash_aliases
pcapture_start
pcapture_status
```

4. During market:

```bash
pcheck
pcapture_status
```

5. At market close:

```bash
pcapture_stop
pseal
```

## Safety

The recorder is read-only. It reads Redis streams and writes compressed JSONL files. It does not start risk, execution, broker order, paper/live, or Redis delete.
