# Batch 26-O18 — Lightweight Controlled-Paper Preflight

## Purpose

O18 is a preflight only. It proves whether the system is ready for a later controlled-paper retry after O17B-R2 passed.

## Hard Safety Boundary

This batch does not:

- start paper,
- start risk,
- start execution,
- call broker,
- write orders,
- approve real live,
- run a heavy monitor,
- run Redis XREVRANGE loops,
- force candidates,
- relax thresholds.

## Required PASS

`PASS_O18_LIGHTWEIGHT_CONTROLLED_PAPER_PREFLIGHT_OK`

Only then proceed to O19.

## O19 Scope If O18 Passes

- MIST CALL only
- 1 lot only
- real-live false
- no automatic broker failover
- no mid-position provider migration
- no heavy O11 monitor
- lightweight duration and lightweight health checks only
