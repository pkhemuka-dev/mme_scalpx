# Batch 26-O19 — Lightweight Controlled-Paper Runtime Start

## Purpose

O19 starts a bounded controlled-paper runtime after O18 preflight PASS.

## Scope

- MIST CALL only
- 1 lot only
- controlled paper/sandbox only
- real-live false
- no automatic broker failover
- no mid-position provider migration
- no heavy monitor
- no Redis XREVRANGE loops
- no threshold relaxation
- no forced candidate

## Services

The script starts only missing services among:

- feeds
- features
- strategy
- risk
- execution

It stops only the services it started.

## Required PASS

`PASS_O19_LIGHTWEIGHT_CONTROLLED_PAPER_RUNTIME_OK_NO_ORDER`

If PASS, next batch is O20 extended controlled-paper observation with bounded lightweight monitoring.

If FAIL, inspect proof JSON and logs; do not continue.
