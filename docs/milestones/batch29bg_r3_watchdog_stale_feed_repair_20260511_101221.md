# Batch 29BG-R3 — watchdog stale-feed repair hardening — 20260511_101221

## Problem
Watchdog existed but did not repair stale feed loop:
- visible feed process lost lock
- lock:feeds owner differed or disappeared
- pfeeds log spammed feeds singleton lock refresh failed
- errors stream grew rapidly

## Fix
- phealth_safe.py detects latest pfeeds log containing feeds singleton lock refresh failed.
- That condition is safe-feed-repairable when Redis is PONG/loading=0/blocked_clients=0, orders=0, and risk/execution are absent.
- REDIS_MEMORY_HIGH remains visible but no longer blocks stale-feed repair by itself.
- prepair_safe.py now repairs feed-only:
  - stops feed processes only
  - clears lock:feeds
  - clears stale lock:execution only if execution process absent
  - removes pfeeds.pid only
  - starts feeds only through pfeeds --force-all

## Safety
- No risk/execution start
- No paper/live enablement
- No Redis restart
- No order sending
- No model/doctrine/strategy patch

## Proofs
- run/proofs/batch29bg_r3_watchdog_stale_feed_repair_20260511_101221_compile.txt
- run/proofs/batch29bg_r3_watchdog_stale_feed_repair_20260511_101221_phealth_before.json
- run/proofs/batch29bg_r3_watchdog_stale_feed_repair_20260511_101221_pwatch_once_repair.json
- run/proofs/batch29bg_r3_watchdog_stale_feed_repair_20260511_101221_phealth_after.json
- run/proofs/batch29bg_r3_watchdog_stale_feed_repair_20260511_101221_pfeedcheck_after.txt
