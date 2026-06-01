# B1-PROFIT-LIVE-R37B_CAPTURE_SUPERVISOR_INSTALL_NO_ORDER

## Purpose

Install an observe-only capture supervisor for next live session.

## Allowed automatic actions

- start durable recorder
- start features if missing
- start strategy if missing
- start feeds if fut/opt stream freshness is stale

## Forbidden actions

- no risk start
- no execution start
- no paper/live/broker order
- no Redis delete
- no source patch during live session

## Helpers

```bash
source ~/.bash_aliases
pauto_plan
pauto_start
pauto_status
pauto_stop
```

## Tomorrow flow

```bash
source ~/.bash_aliases
pauto_plan
pauto_start
pauto_status
pcheck
pcapture_status
```
